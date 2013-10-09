Ext.ns("go");

function show_progress_dialog(dlg_title, dlg_msg, dlg_width, close_on_100, dlg_text){
    Ext.MessageBox.show({
                        title       : dlg_title, //消息框标题
                        msg         : dlg_msg,   //显示的文本
                        width       : 240,       //宽度
                        progress    : true,      //此属性证明是滚动条
                        closable    : false,     //不可以关闭
                        wait        : true,
                        waitConfig  : {interval:600},//0.6s进度条自动加载一定长度
                        animEl      : 'mb6'      //飞出来的
    });
    var f = function(value){
        return function(){
            if( value == 100 && close_on_100 ){
                Ext.MessageBox.hide();
            }else{
                if(dlg_text){
                    Ext.MessageBox.updateProgress(value / 100, dlg_text + '%' + value);
                }
            }
        };
    };
    for(var i = 1; i <= 100; i++){
        setTimeout(f(i), 1000);
    }
}

function show_event_dialog(title, msg, icon, handler){
    if ( ! handler){
        handler = function(btn, text){
                if (btn == 'ok') {
                    document.location = loginUrl;
                }
            }
    }
    Ext.MessageBox.show({
        title: title,
        msg: msg,
        buttons: Ext.Msg.OK,
        icon: icon,
        fn: handler
    });
}

function handle_srv_event(evt){
    // evt格式：
    // { success: true | false,
    //   data: [ { obj : "os",   // 对象名
    //                cmd : 'refresh_grid', 
    //                param:'...'
    //              },
    //              ...
    //         ],
    // }
    if ( ! evt.success )
        return false;
    for(var e in evt.data){
        comp = Ext.getCmp(evt.data[e].obj + 'Panel');
        if ( ! comp || ! evt.data[e].cmd) continue;
        func = "comp." + evt.data[e].cmd + "( evt.data[e].param ); ";
        eval(func);
    }
}

function getSrvEvent(){
    Ext.Ajax.request({
        url: "/srvevt", // 取服务器事件
        disableCaching: true,              //是否禁用缓存,当然要禁用
        timeout: 10000,                    //最大等待时间,超出则会触发超时
        success: function(response, option){
            if (!response || response.responseText == '') {//返回的内容为空,即服务器停止响应时
                Ext.TaskMgr.stop(srv_event_cfg);
                show_event_dialog('错误', '连接状态发生错误，请稍候再次进行登录!', Ext.MessageBox.ERROR);
                return;
            } else {
                result = Ext.decode(response.responseText);
                if (result.success == 'true') {
                    return handle_srv_event(result);
                } else {
                    //Ext.TaskMgr.stop(srv_event_cfg);
                    //show_event_dialog('登录检测','您已经长时间未操作或已经退出登录，请重新登录。', Ext.MessageBox.INFO);
                }
            }
        },
        failure: function(data){//ajax请求发送失败或超时
            Ext.TaskMgr.stop(srv_event_cfg);
            show_event_dialog('错误','在连接服务器时发生网络错误，请确认您已经链接网络后再次进行登录。', Ext.MessageBox.ERROR);
        }
    });
    return true;
};

function log_msg(msg){
    var o = Ext.getCmp('msg_board');
    if (o) o.setText(msg);
}

function handleCallback(requestParams, async_url, wait_result, success_callback, failed_callback) {
	var conn = new Ext.data.Connection();
    if(wait_result){
        show_progress_dialog("请稍候", "操作正在执行...", 300, false);
    }
    log_msg("");
	conn.request({
		url: async_url,
		params: requestParams,
		callback: function(options, success, response ) {
            Ext.MessageBox.hide();
			if( success ) {
				json = Ext.decode( response.responseText );
				if( json.success ) {
					try {
                        if(success_callback){
                            success_callback(json.info);
                        }
					} catch(e) {  }
				} else {
					//Ext.Msg.alert( '出错了', json.err);
                    if (failed_callback) failed_callback(json)
                    log_msg(json.err);
				}
			} else {
                //if (failed_callback) failed_callback(response.responseText);
				//Ext.Msg.alert( 'Error', 'Failed to connect to the server.');
                log_msg('Server error! Failed to connect to the server.');
			}

		}
	});
}
