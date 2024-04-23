


--             UPDATE image_info
--             SET status = 100, wcs_info = '-', center_v_x=0.9022402425401407, center_v_y=0.43110644874989756, center_v_z=-0.010477336844827937, a_v_x=0.9025965671110666, a_v_y=0.43039144658071005, a_v_z=0.00909064076298617,
--             center_a_theta=1.6765122288047962, b_v_x=0.9144476412517257, b_v_y=0.40453580358837493, b_v_z=-0.011674545998155358, center_b_theta=1.121634144504597
--             WHERE id = 1



SELECT id, file_path FROM image_info WHERE status = 1


-- update image_info set status=1 where status = 101

SELECT id, file_path FROM image_info WHERE status = 1  limit 1
SELECT * FROM image_info WHERE status = 100  limit 10

-- t_v = [-0.18536240948083066, 0.9391063563145884, 0.2893441353837993]

select * from image_info where center_a_theta > abs(90-degrees(acos(1))) and center_b_theta > abs(90-degrees(acos(2)))

select * from image_info where
 center_a_theta > abs(90-degrees(acos(((-0.18536240948083066*image_info.a_v_x) +(0.9391063563145884*image_info.a_v_y)+(0.2893441353837993*image_info.a_v_z) ))))
 and
 center_b_theta > abs(90-degrees(acos(((-0.18536240948083066*image_info.b_v_x) +(0.9391063563145884*image_info.b_v_y)+(0.2893441353837993*image_info.b_v_z) ))))

select center_a_theta, acos(((-0.18536240948083066*image_info.a_v_x) +(0.9391063563145884*image_info.a_v_y)+(0.2893441353837993*image_info.a_v_z) )) as ta from  image_info where center_b_theta>ta

select center_b_theta, acos(((-0.18536240948083066*image_info.b_v_x) +(0.9391063563145884*image_info.b_v_y)+(0.2893441353837993*image_info.b_v_z) )) as tb from  image_info where center_b_theta>tb



select center_a_theta, degrees(acos(((-0.18536240948083066*image_info.a_v_x) +(0.9391063563145884*image_info.a_v_y)+(0.2893441353837993*image_info.a_v_z) ))) as ta from  image_info --where center_b_theta>ta

select center_b_theta, degrees(acos(((-0.18536240948083066*image_info.b_v_x) +(0.9391063563145884*image_info.b_v_y)+(0.2893441353837993*image_info.b_v_z) ))) as tb from  image_info where center_b_theta>tb


select center_a_theta, degrees(acos(((-0.18536240948083066*image_info.a_v_x) +(0.9391063563145884*image_info.a_v_y)+(0.2893441353837993*image_info.a_v_z) ))) as ta from  image_info where status=100 order by ta desc --where center_b_theta>ta


select center_a_theta, 90-(degrees(acos(((-0.18536240948083066*image_info.a_v_x) +(0.9391063563145884*image_info.a_v_y)+(0.2893441353837993*image_info.a_v_z) )))) as ta from  image_info where status=100 order by ta --where center_b_theta>ta

select center_a_theta, abs(90-(degrees(acos(((-0.18536240948083066*image_info.a_v_x) +(0.9391063563145884*image_info.a_v_y)+(0.2893441353837993*image_info.a_v_z) ))))) as ta from  image_info where status=100 order by ta  --where center_b_theta>ta
select center_b_theta, abs(90-(degrees(acos(((-0.18536240948083066*image_info.b_v_x) +(0.9391063563145884*image_info.b_v_y)+(0.2893441353837993*image_info.b_v_z) ))))) as tb from  image_info where status=100 order by tb --where center_b_theta>ta
-- null?????
select  center_b_theta, acos(((-0.18536240948083066*image_info.b_v_x) +(0.9391063563145884*image_info.b_v_y)+(0.2893441353837993*image_info.b_v_z) )) as tb, * from  image_info where status=100 and id>82 and id < 90
select  center_b_theta, ((-0.18536240948083066*image_info.b_v_x) +(0.9391063563145884*image_info.b_v_y)+(0.2893441353837993*image_info.b_v_z) )as tb, * from  image_info where status=100 and id>82 and id < 90
select  center_b_theta, ((-0.18536240948083066*image_info.b_v_x) +(0.9391063563145884*image_info.b_v_y)+(0.2893441353837993*image_info.b_v_z) )as tb, * from  image_info where status=100 order by tb desc


select acos(0.9) from image_info where id >82 and id < 90
select acos(1.1) from image_info where id >82 and id < 90
select acos(1) from image_info where id >82 and id < 90



select center_a_theta, abs(90-(degrees(acos(((-0.18536240948083066*image_info.a_v_x) +(0.9391063563145884*image_info.a_v_y)+(0.2893441353837993*image_info.a_v_z) ))))) as ta from  image_info where status=100 and ta not null order by ta  --where center_b_theta>ta
select center_b_theta, abs(90-(degrees(acos(((-0.18536240948083066*image_info.b_v_x) +(0.9391063563145884*image_info.b_v_y)+(0.2893441353837993*image_info.b_v_z) ))))) as tb from  image_info where status=100 and tb not null order by tb  --where center_b_theta>ta


select center_a_theta, abs(90-(degrees(acos(((-0.18536240948083066*image_info.a_v_x) +(0.9391063563145884*image_info.a_v_y)+(0.2893441353837993*image_info.a_v_z) ))))) as ta,
       center_b_theta, abs(90-(degrees(acos(((-0.18536240948083066*image_info.b_v_x) +(0.9391063563145884*image_info.b_v_y)+(0.2893441353837993*image_info.b_v_z) ))))) as tb
from  image_info where status=100 and ta not null and  center_a_theta>ta and center_b_theta>tb

select center_a_theta, abs(90-(degrees(acos(((-0.18536240948083066*image_info.a_v_x) +(0.9391063563145884*image_info.a_v_y)+(0.2893441353837993*image_info.a_v_z) ))))) as ta from  image_info where status=100 and ta not null and  center_a_theta>ta order by ta
select center_b_theta, abs(90-(degrees(acos(((-0.18536240948083066*image_info.b_v_x) +(0.9391063563145884*image_info.b_v_y)+(0.2893441353837993*image_info.b_v_z) ))))) as tb from  image_info where status=100 and tb not null and center_b_theta>tb order by tb

select count(*) from (select center_a_theta, abs(90-(degrees(acos(((-0.18536240948083066*image_info.a_v_x) +(0.9391063563145884*image_info.a_v_y)+(0.2893441353837993*image_info.a_v_z) ))))) as ta from  image_info where status=100 and ta not null and  center_a_theta>ta order by ta)
select center_b_theta, abs(90-(degrees(acos(((-0.18536240948083066*image_info.b_v_x) +(0.9391063563145884*image_info.b_v_y)+(0.2893441353837993*image_info.b_v_z) ))))) as tb from  image_info where status=100 and tb not null and center_b_theta>tb order by tb




select center_a_theta, abs(90-(degrees(acos(((-0.18536240948083066*image_info.a_v_x) +(0.9391063563145884*image_info.a_v_y)+(0.2893441353837993*image_info.a_v_z) ))))) as ta,
       center_b_theta, abs(90-(degrees(acos(((-0.18536240948083066*image_info.b_v_x) +(0.9391063563145884*image_info.b_v_y)+(0.2893441353837993*image_info.b_v_z) ))))) as tb
from  image_info where status=100 and ta not null and  center_a_theta>ta and center_b_theta>tb

-- [-0.7340666984702854, 0.25515079385691664, 0.6293203910498374]
select center_a_theta, abs(90-(degrees(acos(((-0.7340666984702854*image_info.a_v_x) +(0.25515079385691664*image_info.a_v_y)+(0.6293203910498374*image_info.a_v_z) ))))) as ta,
       center_b_theta, abs(90-(degrees(acos(((-0.7340666984702854*image_info.b_v_x) +(0.25515079385691664*image_info.b_v_y)+(0.6293203910498374*image_info.b_v_z) ))))) as tb,
       *
from  image_info where status=100 and ta not null and  center_a_theta>ta and center_b_theta>tb order by  ta


select center_a_theta, abs(90-(degrees(acos(((-0.7340666984702854*image_info.a_n_x) +(0.25515079385691664*image_info.a_n_y)+(0.6293203910498374*image_info.a_n_z) ))))) as ta,
       center_b_theta, abs(90-(degrees(acos(((-0.7340666984702854*image_info.b_n_x) +(0.25515079385691664*image_info.b_n_y)+(0.6293203910498374*image_info.b_n_z) ))))) as tb,
       *
from  image_info where status=100 and ta not null and  center_a_theta>ta and center_b_theta>tb order by  ta

select * from image_info where  file_path like '%K028%'
select a_n_x,a_n_y,a_n_z,b_n_x,b_n_y,b_n_z,* from image_info where id = 3829

select center_a_theta, abs(90-(degrees(acos(((-0.7340666984702854*image_info.a_n_x) +(0.25515079385691664*image_info.a_n_y)+(0.6293203910498374*image_info.a_n_z) ))))) as ta,
       center_b_theta, abs(90-(degrees(acos(((-0.7340666984702854*image_info.b_n_x) +(0.25515079385691664*image_info.b_n_y)+(0.6293203910498374*image_info.b_n_z) ))))) as tb,
       *
from  image_info where status=100 and id = 3829 order by  ta

select center_a_theta, abs(90-(degrees(acos(((-0.7340666984702854*image_info.a_n_x) +(0.25515079385691664*image_info.a_n_y)+(0.6293203910498374*image_info.a_n_z) ))))) as ta,
       center_b_theta, abs(90-(degrees(acos(((-0.7340666984702854*image_info.b_n_x) +(0.25515079385691664*image_info.b_n_y)+(0.6293203910498374*image_info.b_n_z) ))))) as tb,
       *
from  image_info where status=100 and ta not null and  center_a_theta>ta and center_b_theta>tb order by  ta


select t.status, center_a_theta, abs(90-(degrees(acos(((-0.7340666984702854*t.a_n_x) +(0.25515079385691664*t.a_n_y)+(0.6293203910498374*t.a_n_z) ))))) as ta,
       center_b_theta, abs(90-(degrees(acos(((-0.7340666984702854*t.b_n_x) +(0.25515079385691664*t.b_n_y)+(0.6293203910498374*t.b_n_z) ))))) as tb,
       *
from  image_info as t where t.status=100 and tb is null order by  ta



select center_a_theta, abs(90-(degrees(acos(((-0.7340666984702854*t.a_n_x) +(0.25515079385691664*t.a_n_y)+(0.6293203910498374*t.a_n_z) ))))) as ta,
       center_b_theta, abs(90-(degrees(acos(((-0.7340666984702854*t.b_n_x) +(0.25515079385691664*t.b_n_y)+(0.6293203910498374*t.b_n_z) ))))) as tb,
       *
from  image_info as t where id = 3829


-0.7351623107802017, 0.33411621568195654, 0.5898327993818946

select center_a_theta, abs(90-(degrees(acos(((-0.7351623107802017*t.a_n_x) +(0.33411621568195654*t.a_n_y)+(0.5898327993818946*t.a_n_z) ))))) as ta,
       center_b_theta, abs(90-(degrees(acos(((-0.7351623107802017*t.b_n_x) +(0.33411621568195654*t.b_n_y)+(0.5898327993818946*t.b_n_z) ))))) as tb,
       *
from  image_info as t where t.status=100 and t.center_a_theta>ta and t.center_b_theta>tb and file_path not like '%K028%'


