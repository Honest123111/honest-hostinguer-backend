WITH fk_info AS (
    SELECT array_to_string(array_agg(
        CONCAT(
            '{"schema":"', trim(both '"' from schema_name), '"',
            ',"table":"', trim(both '"' from table_name::text), '"',
            ',"column":"', trim(both '"' from fk_column::text), '"',
            ',"foreign_key_name":"', foreign_key_name, '"',
            ',"reference_schema":"', COALESCE(reference_schema, 'public'), '"',
            ',"reference_table":"', reference_table, '"',
            ',"reference_column":"', reference_column, '"',
            ',"fk_def":"', replace(fk_def, '"', ''),
            '"}'
        )), ',') as fk_metadata
    FROM (
        SELECT c.conname AS foreign_key_name,
               n.nspname AS schema_name,
               CASE WHEN position('.' in conrelid::regclass::text) > 0
                    THEN split_part(conrelid::regclass::text, '.', 2)
                    ELSE conrelid::regclass::text
               END AS table_name,
               a.attname AS fk_column,
               nr.nspname AS reference_schema,
               CASE WHEN position('.' in confrelid::regclass::text) > 0
                    THEN split_part(confrelid::regclass::text, '.', 2)
                    ELSE confrelid::regclass::text
               END AS reference_table,
               af.attname AS reference_column,
               pg_get_constraintdef(c.oid) as fk_def
        FROM pg_constraint AS c
        JOIN pg_attribute AS a ON a.attnum = ANY(c.conkey) AND a.attrelid = c.conrelid
        JOIN pg_class AS cl ON cl.oid = c.conrelid
        JOIN pg_namespace AS n ON n.oid = cl.relnamespace
        JOIN pg_attribute AS af ON af.attnum = ANY(c.confkey) AND af.attrelid = c.confrelid
        JOIN pg_class AS clf ON clf.oid = c.confrelid
        JOIN pg_namespace AS nr ON nr.oid = clf.relnamespace
        WHERE c.contype = 'f'
          AND connamespace::regnamespace::text NOT IN ('information_schema', 'pg_catalog')
    ) AS x
)
SELECT fk_metadata FROM fk_info;
