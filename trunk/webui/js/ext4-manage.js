Ext.BLANK_IMAGE_URL = '../ext/resources/images/default/s.gif';
Ext.QuickTips.init();
var main, menu, header;
var mb_product_name="小迈学围棋";
var srv_event_cfg;
var xiti_loaded = 0;

Ext.onReady(function() {
    show_main_panel();
});


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
}

Ext.define("Ext.FlashPanel", {
    extend: "Ext.Panel"
    ,alias: "FlashPanel"
    ,id : 'flash_panel'
    ,autoScroll : true
    ,title : '练习'
    ,closable : false
    ,layout: 'fit'
    ,listeners:{'afterlayout': function(o, opt){
                                  load_goxiti_swf(); 
                              }
    }
});


function load_goxiti_swf() {
    if (xiti_loaded != 0){
        return;
    }
    var attributes = { };
    var flashvars = {
        frame:1,
        ruler:0,
        script:1,
        sgfurl: "./sgf/xiti2.sgf",
    };
    var params =  {
        bgcolor: "#869ca7",
        allowScriptAccess: 'always',
        quality: 'high'
    };
    var p = Ext.getCmp("flash_panel");
    //var p = Ext.getCmp("goxiti_swf");
    var wid = p.getWidth(); 
    var hei = p.getHeight();
    swfobject.embedSWF("js/goxiti.swf", "flash_panel", ""+wid, ""+hei, "9.0.0","expressInstall.swf", flashvars, params, attributes);
    xiti_loaded = 1;
}

Ext.define("go.MainPanel", { 
    extend: "Ext.TabPanel",
    alias: "MainPanel",
    id : 'main',
    region : 'center',
    margins : '0 5 5 0',
    resizeTabs : true,
    minTabWidth : 165,
    tabWidth : 165,
    tabHeight: 500,
    enableTabScroll : true,
    activeTab : 0,
    listeners:{'destroy': function(panel){
                    var o = (typeof panel == "string" ? panel : id || panel.id);
                    var tab = this.getComponent(o);
                    if (tab) {
                        this.remove(tab);
                        tab = null;
                    }
                }
              },
    // ##TODO goxiti.swf bug, this style can not change sgf dynamically
    /*
    items : [{ id: 'goxiti_swf', 
                xtype: 'flash', 
                url: 'js/goxiti.swf',
                flashVars : {
                    frame:1,
                    ruler:0,
                    script:1,
                    sgfurl: "./sgf/xiti1.sgf",
                },
                flashParams: {
                    bgcolor: "#869ca7",
                    allowScriptAccess: 'always',
                    quality: 'high'
                },
             }]
    */
    items : [ new Ext.FlashPanel ],
});

function get_prev_xiti(){
    var mySwf = Ext.getCmp("goxiti_swf");
    //var mySwf = document.getElementById("goxiti_swf");
    var sgfurl = "sgf/xiti1.sgf"; 
    var o = document.getElementById("flash_panel");
    //mySwf.swf.show();
    //mySwf.swf.repaint();
    o.NewGoExercises(sgfurl);
    //mySwf.NewGoExercisesSound(sgfurl,sndurl);//这个函数可以在装载棋谱的时候播放一段音频解说
    /*
    var IndexID = index + 1;
    xitiIndex.innerHTML="第"+IndexID.toString()+ "题";
    */
}

function OnUserPlayMove(x, y, color){
   //Ext.MessageBox.alert('alert', "x=" + x + ", y=" + y );
}


function get_next_xiti() {


}    


function show_main_panel(){
    Ext.apply(Ext.form.VTypes,{
        password:function(val, field){
           if(field.confirmTo){
               var pwd=Ext.get(field.confirmTo);
               return (val==pwd.getValue());
           }
           return true;
        }
    });
    header = new Ext.Panel( {
        border : true,
        region : 'north',
        height : 29,
//        html   : '<div id=topFrame><p>这里放些你需要的东西</p></div>',
 
        tools: [
            {type:'toggle',handler: function(){
            // 点击事件写在这里
             }},
            {type:'close'},
            {type:'restore'},
            {type:'down'},
            {type:'refresh'},
            {type:'minus'},
            {type:'help'},
        ],
        tbar:[{ id:'logout_system', 
                iconCls:'logoutIconCss',
                width: 180,
                text: '  退出登录  ', 
                //handler: logout_button_handler 
             },
              '->',//'->'代表让工具栏按钮到右边去
              //,'->'
              //,this.version_label
             ]
    });
    menu = new go.MenuPanel();
    main = new go.MainPanel({
                bbar:[{ id:'prev_xiti', 
                        iconCls:'logoutIconCss',
                        width: 80,
                        text: '上一题', 
                        handler: get_prev_xiti 
                      },
                      { id:'current_xiti', 
                        xtype: 'textfield',
                        width: 80,
                        name: 'name',
                        text: '上一题', 
                        allowBlank: false  // requires a non-empty value
                      },
                      { id:'next_xiti', 
                        iconCls:'logoutIconCss',
                        width: 80,
                        text: '下一题', 
                        handler: get_next_xiti 
                      },
                    ],
               });
    //布局
    var mgmtwin = new Ext.Window( {
        layout : 'border',
        closable : false,
        draggable: true,
        resizable: true, 
        maximizable : true,
        minimizable : true,
        width    : 1000,
        height   : 600,
        title    : mb_product_name,
        items    : [header, menu, main]
    });
    mgmtwin.show();
    main.addListener('beforetabchange', 
                     function(mainTabPanel, newTab, currentTab){
                        newTab.refresh();
                        if(newTab.addon_refresh){
                            // 放到这里的原因是：
                            // pitPanel的主panel刷新时会导致，pittree重复刷新。
                            newTab.addon_refresh();
                        }
                     }, 
                     this);
    srv_event_cfg = {
        run: getSrvEvent,  //执行任务时执行的函数
        interval: 7 * 1000           //任务间隔，毫秒为单位，这里是7秒
    }
    //Ext.TaskMgr.start(srv_event_cfg);//初始化时就启动任务
}
