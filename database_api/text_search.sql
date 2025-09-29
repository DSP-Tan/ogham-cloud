
SELECT year, page, "text"
FROM english_hl
WHERE to_tsvector('english', "text") @@ plainto_tsquery('english', :'search_term');
