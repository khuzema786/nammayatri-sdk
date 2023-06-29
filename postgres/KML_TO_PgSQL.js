const { readdir, readFile, rm, writeFile, mkdir } = require("fs/promises")
const util = require("util");
const exec = util.promisify(require("child_process").exec);
const { v4: uuidv4 } = require('uuid')
const reader = require("xlsx");

const typeOfMigration = "INSERT" // "INSERT" | "UPDATE"

const kmlDir = __dirname + "/assets/kml";

const pbcopy = (data) => {
    let proc = require('child_process').spawn('pbcopy');
    proc.stdin.write(data);
    proc.stdin.end();
}

(async () => {
    const file = reader.readFile(__dirname + "/assets/specialZone.xlsx");
    const xlsxData = reader.utils.sheet_to_json(file.Sheets[file.SheetNames[0]]);

    const files = [];
    const processDir = async (dirname) => {
        try {
            const items = await readdir(dirname, { withFileTypes: true });
            for (const item of items) {
                if (item.isDirectory()) {
                    await processDir(`${dirname}/${item.name}`);
                } else if (item.name.match(/.*\.kml/gm)) {
                    files.push(`${dirname}/${item.name}`);
                }
            }
        } catch (err) { }
    };
    await processDir(kmlDir);

    let specialLocationMigration = ""
    let fareProductMigration = ""

    const farePolicy = [{
        id: "8cfc6f69-f170-4eee-c1e3-60aaa4a96832",
        variant: 'SEDAN'
    }, {
        id: "c7b11bac-2ceb-f5a2-1b85-c37940a33900",
        variant: 'SUV'
    }, {
        id: "d2ecfe01-d111-bf92-e0dc-616a66da9318",
        variant: 'HATCHBACK'
    }, {
        id: "094112f5-4523-bb76-7697-d6cfd4905361",
        variant: 'AUTO_RICKSHAW'
    }];

    for (let i = 0; i < files.length; i++) {
        try {
            const specialZoneId = uuidv4();
            await mkdir(`${kmlDir}/temp`, { recursive: true });
            await mkdir(`${kmlDir}/geojson`, { recursive: true });
            await exec(`ogr2ogr -f GeoJSON ${kmlDir}/temp/output.json ${files[i].split(" ").join("\\ ")}`);
            const geoJson3D = JSON.parse(await (await readFile(`${kmlDir}/temp/output.json`)).toString("utf8"));
            const geoJson2D = { ...geoJson3D, features : geoJson3D.features.map(feature => ({ ...feature, geometry : { ...feature.geometry, coordinates : feature.geometry.coordinates.map(coordinate => coordinate.map(coordinate_ => ([coordinate_[0], coordinate_[1]]))) } })) }
            await writeFile(`${kmlDir}/temp/output.json`, JSON.stringify(geoJson2D))
            await exec(`ogr2ogr -f "ESRI Shapefile" ${kmlDir}/temp/output.shp ${kmlDir}/temp/output.json`);
            await exec(`shp2pgsql ${kmlDir}/temp/output.shp > ${kmlDir}/temp/output.sql`)
            const shapeData = await (await readFile(`${kmlDir}/temp/output.sql`)).toString("utf8");
            // console.log(shapeData)
            const geometry = (/INSERT INTO .* VALUES \(.*'(.*)'\);/gm).exec(shapeData)[1];
            let xlsxFilteredData = xlsxData.filter(el => el['Metro stations'] + ".kml" === files[i].split("/")[files[i].split("/").length - 1])
            if (xlsxFilteredData.length === 0) throw "Name Not Matched"
            await writeFile(`${kmlDir}/geojson/${xlsxFilteredData[0]['Wiki Name']}.json`, JSON.stringify(geoJson2D))

            if (typeOfMigration === "INSERT") {
                specialLocationMigration += `INSERT INTO atlas_driver_offer_bpp.special_location (id, location_name, category, gates, geom, created_at)
    VALUES
    ( '${specialZoneId}'
    , '${xlsxFilteredData[0]['Wiki Name']}'
    , 'SureMetro'
    , '{}'
    , '${geometry}'
    , now()
    );\n`

                fareProductMigration += farePolicy.map(({ id, variant }) =>
                    `INSERT INTO atlas_driver_offer_bpp.fare_product (id, merchant_id, fare_policy_id, vehicle_variant, "area", flow) VALUES ('${uuidv4()}','7f7896dd-787e-4a0b-8675-e9e6fe93bb8f','${id}','${variant}','Pickup_${specialZoneId}','NORMAL');\nINSERT INTO atlas_driver_offer_bpp.fare_product (id, merchant_id, fare_policy_id, vehicle_variant, "area", flow) VALUES ('${uuidv4()}','7f7896dd-787e-4a0b-8675-e9e6fe93bb8f','${id}','${variant}','Drop_${specialZoneId}','NORMAL');\n`).join("");
            } else if (typeOfMigration === "UPDATE") {
                specialLocationMigration += `UPDATE atlas_driver_offer_bpp.special_location SET geom='${geometry}' WHERE location_name='${xlsxFilteredData[0]['Wiki Name']}';\n`
            }
            console.log(`done : ${files[i]}`);
        } catch (err) {
            console.log(`skipped : ${files[i]}`, err);
            continue;
        } finally {
            await rm(`${kmlDir}/temp`, { recursive: true, force: true });
        }
    }
    await rm(`${kmlDir}/temp`, { recursive: true, force: true });
    await rm(__dirname + "/assets/migrations", { recursive: true, force: true });
    // pbcopy(migration);
    await mkdir(__dirname + "/assets/migrations", { recursive: true });
    await writeFile(__dirname + "/assets/migrations/special-location.sql", specialLocationMigration)
    await writeFile(__dirname + "/assets/migrations/fare-product.sql", fareProductMigration)
})()