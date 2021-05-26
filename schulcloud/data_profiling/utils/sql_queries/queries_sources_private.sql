select `space.ccm:replicationsource_DISPLAYNAME` as source, count(*) as `count`
from data
group by `space.ccm:replicationsource_DISPLAYNAME`
order by `count` desc