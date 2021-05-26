select `lom.general.description`, length(`lom.general.description`) as len, count(*) as cnt
from data
group by `lom.general.description`
order by cnt desc
