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

FT.DROPINDEX idx:rpg:cryptids
FT.CREATE idx:rpg:cryptids                              
    ON HASH                                           
        PREFIX 1 rpg:cryptids:      
    SCHEMA
        notion_id AS notion_id TEXT WEIGHT 1.0
        deep_level AS deep_level TEXT WEIGHT 1.0              
        status AS status TEXT WEIGHT 1.0  
        npc as npc TEXT WEIGHT 1.0  

FT.DROPINDEX idx:rpg:cryptidshp
FT.CREATE idx:rpg:cryptidshp                            
    ON HASH                                           
        PREFIX 1 rpg:cryptids:      
    SCHEMA
        notion_id AS notion_id TEXT WEIGHT 1.0
        hp AS hp NUMERIC 
        max_hp AS max_hp NUMERIC