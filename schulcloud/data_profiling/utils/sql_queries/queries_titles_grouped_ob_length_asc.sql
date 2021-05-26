select `lom.general.title`, length(`lom.general.title`) as len, count(*) as cnt
from data
group by `lom.general.title`
order by len asc