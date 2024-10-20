{% macro test_positive_value(model, column_name) %}
    -- This macro tests if all values in the specified column are greater than or equal to 0
    WITH validation AS (
        SELECT
            {{ column_name }} AS value
        FROM {{ model }}
        WHERE {{ column_name }} < 0
    )
    SELECT COUNT(*) AS failures
    FROM validation
{% endmacro %}
