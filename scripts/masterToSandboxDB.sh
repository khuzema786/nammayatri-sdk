#!/bin/bash

# Database credentials
DB_USER="atlas_rw"
DB_HOST="beckn-test-integ-aurora.ctiuwghisbi9.ap-south-1.rds.amazonaws.com"
DB_PORT=5432
LIMIT=5000

# Atlas Driver Offer BPP
FROM_DB_NAMES=("atlas_driver_offer_bpp_v2" "atlas_app_v2")
TO_DB_NAMES=("atlas_driver_offer_bpp" "atlas_app")
SCHEMA_NAMES=("atlas_driver_offer_bpp" "atlas_app")

TABLE_TO_MIGRATE_FULLY=("person driver_flow_status driver_information driver_location vehicle" "person")

# Tables to apply updates to
GATEWAY_TABLES=("merchant")

# Prompt for password securely
read -s -p "Enter database password: " DB_PASS
echo

for ((i=0; i<${#FROM_DB_NAMES[@]}; i++)); do
    FROM_DB_NAME="${FROM_DB_NAMES[i]}"
    TO_DB_NAME="${TO_DB_NAMES[i]}"
    SCHEMA_NAME="${SCHEMA_NAMES[i]}"

    for TABLE in $(PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $FROM_DB_NAME -t -c "SELECT table_name FROM information_schema.tables WHERE table_schema = '$SCHEMA_NAME';"); do
        rm -rf "dumps"
        mkdir -p "dumps"
        
        PGPASSWORD=$DB_PASS pg_dump -h $DB_HOST -p $DB_PORT -d $FROM_DB_NAME -U $DB_USER -t $SCHEMA_NAME.$TABLE -s -f "dumps/schema_$TABLE"
        
        # Check if the 'created_at' column exists in the table
        PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $FROM_DB_NAME -c "SELECT column_name FROM information_schema.columns WHERE table_name = '$TABLE' AND column_name = 'created_at';" | grep -q "created_at"
        HAS_CREATED_AT=$?
        
        if [ $HAS_CREATED_AT -eq 0 ]; then
            # 'created_at' column exists, export sorted data to CSV using \COPY
            PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $FROM_DB_NAME -c "\COPY (SELECT * FROM $SCHEMA_NAME.$TABLE ORDER BY created_at DESC LIMIT $LIMIT) TO 'dumps/table_$TABLE' WITH CSV HEADER;"
        else
            # 'created_at' column does not exist, export data to CSV without sorting using \COPY
            PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $FROM_DB_NAME -c "\COPY (SELECT * FROM $SCHEMA_NAME.$TABLE LIMIT $LIMIT) TO 'dumps/table_$TABLE' WITH CSV HEADER;"
        fi

        # Delete the table in the target database
        PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $TO_DB_NAME -c "DROP TABLE IF EXISTS $SCHEMA_NAME.$TABLE CASCADE;"
        
        # Create the table in the target database
        PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $TO_DB_NAME -f "dumps/schema_$TABLE"

        # Import data from CSV into the target database using \COPY
        PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $TO_DB_NAME -c "\COPY $SCHEMA_NAME.$TABLE FROM 'dumps/table_$TABLE' WITH CSV HEADER;"

        # Grant SELECT privileges to beckn_pgweb_ro
        PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $TO_DB_NAME -c "GRANT SELECT ON TABLE $SCHEMA_NAME.$TABLE TO beckn_pgweb_ro;"

        # Check if the query was successful
        if [ $? -eq 0 ]; then
            echo "✅ Granted SELECT privilege on $TABLE to beckn_pgweb_ro."
        else
            echo "❌ Failed to grant SELECT privilege on $TABLE to beckn_pgweb_ro."
        fi

        # Additional Updates
        if [ "$SCHEMA_NAME" == "atlas_driver_offer_bpp" ]; then
            if [[ " ${GATEWAY_TABLES[@]} " =~ " $TABLE " ]]; then
                # Update subscriber_id column to remove "/dev"
                PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $TO_DB_NAME -c "UPDATE $SCHEMA_NAME.$TABLE SET subscriber_id = REPLACE(subscriber_id, '/dev', '');"
            fi
        elif [ "$SCHEMA_NAME" == "atlas_app" ]; then
            if [[ " ${GATEWAY_TABLES[@]} " =~ " $TABLE " ]]; then
                # Update bap_id column to remove "/dev"
                PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $TO_DB_NAME -c "UPDATE $SCHEMA_NAME.$TABLE SET bap_id = REPLACE(bap_id, '/dev', '');"
                # Update gateway_url column to remove "/dev"
                PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $TO_DB_NAME -c "UPDATE $SCHEMA_NAME.$TABLE SET gateway_url = REPLACE(gateway_url, '/dev', '');"
                # Update registry_url column to remove "/dev"
                PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $TO_DB_NAME -c "UPDATE $SCHEMA_NAME.$TABLE SET registry_url = REPLACE(registry_url, '/dev', '');"
            fi
        fi

        if [ $? -eq 0 ]; then
            echo "✅ Exported and inserted data for $TABLE successfully."
        else
            echo "❌ Failed to export and insert data for $TABLE."
        fi
    done

    for TABLE in ${TABLE_TO_MIGRATE_FULLY[i]}; do
        rm -rf "dumps"
        mkdir -p "dumps"

        PGPASSWORD=$DB_PASS pg_dump -h $DB_HOST -p $DB_PORT -d $FROM_DB_NAME -U $DB_USER -t $SCHEMA_NAME.$TABLE -s -f "dumps/schema_$TABLE"
        
        PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $FROM_DB_NAME -c "\COPY (SELECT * FROM $SCHEMA_NAME.$TABLE) TO 'dumps/table_$TABLE' WITH CSV HEADER;"

        PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $TO_DB_NAME -c "DROP TABLE IF EXISTS $SCHEMA_NAME.$TABLE CASCADE;"
        
        PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $TO_DB_NAME -f "dumps/schema_$TABLE"

        PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $TO_DB_NAME -c "\COPY $SCHEMA_NAME.$TABLE FROM 'dumps/table_$TABLE' WITH CSV HEADER;"
    done
done

# Clear Invalid Entries For Atlas Driver Offer BPP
SQL_QUERIES=(
    "DELETE FROM atlas_driver_offer_bpp.person
    WHERE id NOT IN (
        SELECT T1.id
        FROM atlas_driver_offer_bpp.person AS T1
        INNER JOIN atlas_driver_offer_bpp.driver_information AS T2 ON T1.id = T2.driver_id
        INNER JOIN atlas_driver_offer_bpp.vehicle AS T3 ON T2.driver_id = T3.driver_id
        INNER JOIN atlas_driver_offer_bpp.driver_flow_status AS T4 ON T3.driver_id = T4.person_id
        INNER JOIN atlas_driver_offer_bpp.driver_location AS T5 ON T4.person_id = T5.driver_id
        WHERE (T2.active = true AND T2.mode IS NULL) OR (T2.mode IS NOT NULL AND (T2.mode = 'SILENT' OR T2.mode = 'ONLINE'))
        AND T2.blocked = false
        AND T2.subscribed = true
        AND T2.on_ride = false
        AND T1.unencrypted_mobile_number IS NOT NULL
    );"
    "DELETE FROM atlas_driver_offer_bpp.driver_information
    WHERE driver_id NOT IN (
        SELECT T1.id
        FROM atlas_driver_offer_bpp.person AS T1
        INNER JOIN atlas_driver_offer_bpp.driver_information AS T2 ON T1.id = T2.driver_id
        INNER JOIN atlas_driver_offer_bpp.vehicle AS T3 ON T2.driver_id = T3.driver_id
        INNER JOIN atlas_driver_offer_bpp.driver_flow_status AS T4 ON T3.driver_id = T4.person_id
        INNER JOIN atlas_driver_offer_bpp.driver_location AS T5 ON T4.person_id = T5.driver_id
        WHERE (T2.active = true AND T2.mode IS NULL) OR (T2.mode IS NOT NULL AND (T2.mode = 'SILENT' OR T2.mode = 'ONLINE'))
        AND T2.blocked = false
        AND T2.subscribed = true
        AND T2.on_ride = false
        AND T1.unencrypted_mobile_number IS NOT NULL
    );"
    "DELETE FROM atlas_driver_offer_bpp.vehicle
    WHERE driver_id NOT IN (
        SELECT T1.id
        FROM atlas_driver_offer_bpp.person AS T1
        INNER JOIN atlas_driver_offer_bpp.driver_information AS T2 ON T1.id = T2.driver_id
        INNER JOIN atlas_driver_offer_bpp.vehicle AS T3 ON T2.driver_id = T3.driver_id
        INNER JOIN atlas_driver_offer_bpp.driver_flow_status AS T4 ON T3.driver_id = T4.person_id
        INNER JOIN atlas_driver_offer_bpp.driver_location AS T5 ON T4.person_id = T5.driver_id
        WHERE (T2.active = true AND T2.mode IS NULL) OR (T2.mode IS NOT NULL AND (T2.mode = 'SILENT' OR T2.mode = 'ONLINE'))
        AND T2.blocked = false
        AND T2.subscribed = true
        AND T2.on_ride = false
        AND T1.unencrypted_mobile_number IS NOT NULL
    );"
    "DELETE FROM atlas_driver_offer_bpp.driver_flow_status
    WHERE person_id NOT IN (
        SELECT T1.id
        FROM atlas_driver_offer_bpp.person AS T1
        INNER JOIN atlas_driver_offer_bpp.driver_information AS T2 ON T1.id = T2.driver_id
        INNER JOIN atlas_driver_offer_bpp.vehicle AS T3 ON T2.driver_id = T3.driver_id
        INNER JOIN atlas_driver_offer_bpp.driver_flow_status AS T4 ON T3.driver_id = T4.person_id
        INNER JOIN atlas_driver_offer_bpp.driver_location AS T5 ON T4.person_id = T5.driver_id
        WHERE (T2.active = true AND T2.mode IS NULL) OR (T2.mode IS NOT NULL AND (T2.mode = 'SILENT' OR T2.mode = 'ONLINE'))
        AND T2.blocked = false
        AND T2.subscribed = true
        AND T2.on_ride = false
        AND T1.unencrypted_mobile_number IS NOT NULL
    );"
    "DELETE FROM atlas_driver_offer_bpp.driver_location
    WHERE driver_id NOT IN (
        SELECT T1.id
        FROM atlas_driver_offer_bpp.person AS T1
        INNER JOIN atlas_driver_offer_bpp.driver_information AS T2 ON T1.id = T2.driver_id
        INNER JOIN atlas_driver_offer_bpp.vehicle AS T3 ON T2.driver_id = T3.driver_id
        INNER JOIN atlas_driver_offer_bpp.driver_flow_status AS T4 ON T3.driver_id = T4.person_id
        INNER JOIN atlas_driver_offer_bpp.driver_location AS T5 ON T4.person_id = T5.driver_id
        WHERE (T2.active = true AND T2.mode IS NULL) OR (T2.mode IS NOT NULL AND (T2.mode = 'SILENT' OR T2.mode = 'ONLINE'))
        AND T2.blocked = false
        AND T2.subscribed = true
        AND T2.on_ride = false
        AND T1.unencrypted_mobile_number IS NOT NULL
    );"
)

# Loop through the SQL queries and execute them
for SQL_QUERY in "${SQL_QUERIES[@]}"; do
    PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d "atlas_driver_offer_bpp" -c "$SQL_QUERY"
    if [ $? -eq 0 ]; then
        echo "✅ Query executed successfully."
    else
        echo "❌ Query execution failed."
    fi
done