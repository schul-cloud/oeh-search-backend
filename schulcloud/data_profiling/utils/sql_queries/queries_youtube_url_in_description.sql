select *
from data
where (`lom.technical.location` like "%https://www.youtube.com%" or `lom.technical.location` like "%http://www.youtube.com%") and `space.ccm:replicationsourceorigin_DISPLAYNAME` <> "['Youtube']"
order by `space.ccm:replicationsourceorigin_DISPLAYNAME` asc