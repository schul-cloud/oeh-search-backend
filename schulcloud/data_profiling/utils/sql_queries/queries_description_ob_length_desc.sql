select `lom.general.description`, length(`lom.general.description`) as LEN, count(*) as cnt
from data
group by `lom.general.description`
order by LEN desc
