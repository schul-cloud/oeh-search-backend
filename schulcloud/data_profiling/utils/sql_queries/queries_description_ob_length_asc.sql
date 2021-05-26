select `lom.general.description` as `description`, length(`lom.general.description`) as `length`, count(*) as `count`
from data
group by `lom.general.description`
order by `length` asc
