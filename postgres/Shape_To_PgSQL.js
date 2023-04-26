const { readdir, readFile, rm, writeFile, mkdir } = require("fs/promises")
const util = require("util");
const exec = util.promisify(require("child_process").exec);
const {v4 : uuidv4} = require('uuid')
const reader = require("xlsx");

const shapesDir = __dirname + "/assets/shapes";

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
            } else if (item.name.match(/.*\.zip/gm)) {
                files.push(`${dirname}/${item.name}`);
            }
        }
        } catch (err) { }
    };
    await processDir(shapesDir);

    let specialLocationMigration = ""
    let fareProductMigration = ""

    const vehicleVariants = ['SEDAN', 'SUV', 'HATCHBACK', 'AUTO_RICKSHAW'];
    const fareProductIds = ['dfa71068-e360-4250-9e94-4fcde4108ppf', '8999b33b-4ee7-4094-b18e-ee44f759dppf', '46086ed6-2c89-4395-ad4a-3d51c90ebppf', '08f1eb60-2143-4558-b6b1-4e56a7f09ppf'];

    for (let i = 0; i < files.length; i++) {
        try {
            const specialZoneId = uuidv4();
            await rm(`${shapesDir}/temp`, { recursive: true, force: true });
            await exec(`unzip ${files[i].split(" ").join("\\ ")} -d ${shapesDir}/temp`);
            await exec(`shp2pgsql ${shapesDir}/temp/layers/POLYGON.shp > ${shapesDir}/temp/temp.sql`)
            const shapeData = await (await readFile(`${shapesDir}/temp/temp.sql`)).toString("utf8");
            // console.log(shapeData)
            const geometry = (/INSERT INTO .* VALUES \(.*'(.*)'\);/gm).exec(shapeData)[1];
            let xlsxFilteredData = xlsxData.filter(el => el['Metro stations'] + ".zip" === files[i].split("/")[files[i].split("/").length - 1])
            if(xlsxFilteredData.length === 0) throw "Name Not Matched"
            specialLocationMigration += `INSERT INTO atlas_driver_offer_bpp.special_location (id, location_name, category, gates, geom, created_at)
    VALUES
    ( '${specialZoneId}'
    , '${xlsxFilteredData[0]['Wiki Name']}'
    , 'SureMetro'
    , '{}'
    , '${geometry}'
    , now()
    );\n`

            fareProductMigration += vehicleVariants.map((vehVar, i) => 
                `INSERT INTO atlas_driver_offer_bpp.special_zone_link VALUES ('${uuidv4()}','${specialZoneId}','favorit0-0000-0000-0000-00000favorit','${fareProductIds[i]}','${vehVar}','PICKUP');\nINSERT INTO atlas_driver_offer_bpp.special_zone_link VALUES ('${uuidv4()}','${specialZoneId}','favorit0-0000-0000-0000-00000favorit','${fareProductIds[i]}','${vehVar}','DROP');\n`).join("");
            
            console.log(`done : ${files[i]}`);
        } catch (err) {
            console.log(`skipped : ${files[i]}`, err);
            continue;
        }
    }
    await rm(`${shapesDir}/temp`, { recursive: true, force: true });
    await rm(__dirname + "/assets/migrations", { recursive: true, force: true });
    // pbcopy(migration);
    await mkdir(__dirname + "/assets/migrations", { recursive: true });
    await writeFile(__dirname + "/assets/migrations/special-location.sql", specialLocationMigration)
    await writeFile(__dirname + "/assets/migrations/fare-product.sql", fareProductMigration)
})()