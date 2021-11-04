




select * from 


授权规则-用户

select p.name, su.name, u.name from perms_assetpermission as p, perms_assetpermission_users as pu, perms_assetpermission_system_users as psu, assets_systemuser as su, users_user as u where p.id in (
    select assetpermission_id from perms_assetpermission_system_users where systemuser_id in (
        select id from assets_systemuser where name in (
            'gateway', 'bosszp', 'athena', 'datastar', 'hdfs'
        )
    )
) 
and p.id = pu.assetpermission_id 
and p.id = psu.assetpermission_id
and pu.user_id = u.id 
and psu.systemuser_id = su.id

授权规则-用户组
select p.name, su.name, u.name  from perms_assetpermission as p, perms_assetpermission_user_groups as pug, perms_assetpermission_system_users as psu, assets_systemuser as su, users_user as u, users_user_groups as ug where p.id in (
    select assetpermission_id from perms_assetpermission_system_users where systemuser_id in (
        select id from assets_systemuser where name in (
            'gateway', 'bosszp', 'athena', 'datastar', 'hdfs'
        )
    )
) 
and p.id = psu.assetpermission_id
and p.id = pug.assetpermission_id 
and pug.usergroup_id = ug.usergroup_id
and ug.user_id = u.id
and psu.systemuser_id = su.id
