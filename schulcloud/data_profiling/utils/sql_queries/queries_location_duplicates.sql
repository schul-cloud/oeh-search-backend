select dpl_locs.*, data.`lom.general.title`, data.`lom.general.description`

-- Get locations that have a count > 1
from (
	SELECT `lom.technical.location`
	
	-- 	Convert HTTPS to HTTP (to catch duplicates across HTTPS and HTTP)
	from (SELECT REPLACE(`lom.technical.location`, 'https','http') as `lom.technical.location` from data)
	group by `lom.technical.location`
	having count(*) > 1
) as dpl_locs inner join data on dpl_locs.`lom.technical.location` = data.`lom.technical.location`

order by `lom.technical.location` asc
