/* 管理WIKI图片资源，第一种：列表中显示图片 */
delete from efClassApple where namespace like 'com.enfo.wiki.images1';
insert into efClassApple(cls_id,namespace,title,listfields,tbname,keycol,enablenew,enableedit,enabledel,orderby,pagination,primarytype)
select '60c859dd758a472c9472ed10b52ed29c','com.enfo.wiki.images1','WIKI图片资源1','IMG_ID|FILEDATA|CREATE_USER|CREATE_TIME|USENUM','WK_IMAGES','IMG_ID',0,0,1,'IMG_ID',1,2
;
update efClassApple set enableview=1, queryfields='FILENAME|FILESIZE|FILEDATA',
    pybeforelist='import json; import web; data = [dict(IMG_ID=x["IMG_ID"],CREATE_USER=x["CREATE_USER"],CREATE_TIME=x["CREATE_TIME"], FILEDATA=json.dumps([x["FILENAME"],x["FILESIZE"],x["FILEDATA"]]), USENUM=web.listget(dbFrame.select("WK_ARTICLES",what="COUNT(*) CNT",vars=locals(),where="ART_CONTENT like \'%%"+x["IMG_ID"]+"%%\'"),0,{}).get("CNT",0)) for x in data]',
    pybeforeview='import json; entityData["FILEDATA"]=json.dumps([entityData["FILENAME"],entityData["FILESIZE"],entityData["FILEDATA"]])'
    where cls_id = '60c859dd758a472c9472ed10b52ed29c';
delete from efPropertyApple where cls_id = '60c859dd758a472c9472ed10b52ed29c';
insert into efPropertyApple(prp_id,cls_id,catalogname,ppname,required,pfield,pformat,is_colspan)
select           'f2abb7edc5054ca9842c4cafb1d86370','60c859dd758a472c9472ed10b52ed29c','','文件名',1,'FILENAME','',0
union all select 'f2abb7edc5054ca9842c4cafb1d86371','60c859dd758a472c9472ed10b52ed29c','','大小',0,'FILESIZE','',0
union all select 'f2abb7edc5054ca9842c4cafb1d86372','60c859dd758a472c9472ed10b52ed29c','','创建人',0,'CREATE_USER','',0
union all select 'f2abb7edc5054ca9842c4cafb1d86373','60c859dd758a472c9472ed10b52ed29c','','创建时间',0,'CREATE_TIME','',0
union all select 'f2abb7edc5054ca9842c4cafb1d86374','60c859dd758a472c9472ed10b52ed29c','','文件内容',0,'FILEDATA','image',0
union all select 'f2abb7edc5054ca9842c4cafb1d86376','60c859dd758a472c9472ed10b52ed29c','','引用',0,'USENUM','',0
;

/* 管理WIKI图片资源，第二种：列表中不显示图片，查看界面显示图片 */
delete from efClassApple where namespace like 'com.enfo.wiki.images2';
insert into efClassApple(cls_id,namespace,title,listfields,tbname,keycol,enablenew,enableedit,enabledel,orderby,pagination,primarytype)
select 'e65f8985d221442dab43370f722affc0','com.enfo.wiki.images2','WIKI图片资源2','IMG_ID|FILENAME|FILESIZE|CREATE_USER|CREATE_TIME|USENUM','WK_IMAGES','IMG_ID',0,0,1,'IMG_ID',1,2
;
update efClassApple set enableview=1,
    pyafterlist='import json; import web; data = [dict(x, USENUM=web.listget(dbFrame.select("WK_ARTICLES",what="COUNT(*) CNT",vars=locals(),where="ART_CONTENT like \'%%"+x["IMG_ID"]+"%%\'"),0,{}).get("CNT",0)) for x in data]',
    pybeforeview='import json; entityData["FILEDATA"]=json.dumps([entityData["FILENAME"],entityData["FILESIZE"],entityData["FILEDATA"]])'
    where cls_id = 'e65f8985d221442dab43370f722affc0';
delete from efPropertyApple where cls_id = 'e65f8985d221442dab43370f722affc0';
insert into efPropertyApple(prp_id,cls_id,catalogname,ppname,required,pfield,pformat,is_colspan)
select           'bf7dee997e624b2cacbe13e150393f40','e65f8985d221442dab43370f722affc0','','文件名',1,'FILENAME','',0
union all select 'bf7dee997e624b2cacbe13e150393f41','e65f8985d221442dab43370f722affc0','','大小',0,'FILESIZE','',0
union all select 'bf7dee997e624b2cacbe13e150393f42','e65f8985d221442dab43370f722affc0','','创建人',0,'CREATE_USER','',0
union all select 'bf7dee997e624b2cacbe13e150393f43','e65f8985d221442dab43370f722affc0','','创建时间',0,'CREATE_TIME','',0
union all select 'bf7dee997e624b2cacbe13e150393f44','e65f8985d221442dab43370f722affc0','','文件内容',0,'FILEDATA','image',0
union all select 'bf7dee997e624b2cacbe13e150393f46','e65f8985d221442dab43370f722affc0','','引用',0,'USENUM','',0
;
