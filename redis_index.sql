FT.DROPINDEX idx:watchlist:movies:byyear                                 
FT.CREATE idx:watchlist:movies:byyear                                 
    ON HASH                                           
        PREFIX 1 watchlist:movies:                             
    SCHEMA
        notion_id AS notion_id TEXT WEIGHT 1.0              
        titulo AS titulo TEXT WEIGHT 1.0              
        anio AS anio NUMERIC  

FT.DROPINDEX idx:watchlist:movies:bystatus                                
FT.CREATE idx:watchlist:movies:bystatus                                 
    ON HASH                                           
        PREFIX 1 watchlist:movies:                             
    SCHEMA
        notion_id AS notion_id TEXT WEIGHT 1.0              
        titulo AS titulo TEXT WEIGHT 1.0              
        estado AS estado TEXT WEIGHT 1.0  

FT.DROPINDEX idx:watchlist:movies:byyearstatus
FT.CREATE idx:watchlist:movies:byyearstatus                                 
    ON HASH                                           
        PREFIX 1 watchlist:movies:                             
    SCHEMA
        notion_id AS notion_id TEXT WEIGHT 1.0              
        titulo AS titulo TEXT WEIGHT 1.0              
        anio AS anio NUMERIC        
        estado AS estado TEXT WEIGHT 1.0  

FT.DROPINDEX idx:watchlist:movies
FT.CREATE idx:watchlist:movies                                 
    ON HASH                                           
        PREFIX 1 watchlist:movies:                             
    SCHEMA
        notion_id AS notion_id TEXT WEIGHT 1.0              
        titulo AS titulo TEXT WEIGHT 1.0              
        anio AS anio NUMERIC        
        estado AS estado TEXT WEIGHT 1.0  

