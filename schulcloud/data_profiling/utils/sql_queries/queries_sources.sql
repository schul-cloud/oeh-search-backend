select `space.ccm:replicationsource_DISPLAYNAME` as source, `space.ccm:replicationsourceorigin_DISPLAYNAME` as sourceorigin, count(*) as `count`
from data
group by `space.ccm:replicationsourceorigin_DISPLAYNAME`, `space.ccm:replicationsource_DISPLAYNAME`
order by `count` desc