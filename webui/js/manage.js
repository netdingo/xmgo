Ext.BLANK_IMAGE_URL = '../ext/resources/images/default/s.gif';
Ext.QuickTips.init();
var main, menu, header;
var mb_product_name="小迈学围棋";
var srv_event_cfg;
var xiti_loaded = 0;
Ext.ns("go");

Ext.onReady(function() {
    show_main_panel();
});

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
    header = new Ext.Panel( { // 目前不用.
        border : true
        ,region : 'north'
        ,height : 29
//        html   : '<div id=topFrame><p>这里放些你需要的东西</p></div>',
//        
        ,tbar:[{ id:'logout_system'
                ,iconCls:'logoutIconCss'
                ,width: 180
                ,text: '  退出登录  '
                //,handler: logout_button_handler 
             }
              //,'->'//'->'代表让工具栏按钮到右边去
              //,'->'
              //,this.version_label
             ]
    });
    menu = new go.MenuPanel();
    main = get_xiti_panel();
    //布局
    var mgmtwin = new Ext.Window( {
        layout : 'border',
        closable : false,
        draggable: false,
        resizable: false, 
        maximizable : false,
        minimizable : false,
        maximized: true,
        /*
        width    : 1000,
        height   : 600,
        */
        title    : mb_product_name,
        items    : [ /*menu, */ main ]
    });
    main.addListener('beforetabchange', 
                     function(mainTabPanel, newTab, currentTab){
                        if(newTab && newTab.refresh){
                            newTab.refresh();
                        }
                        if(newTab && newTab.addon_refresh){
                            // 放到这里的原因是：
                            // pitPanel的主panel刷新时会导致，pittree重复刷新。
                            newTab.addon_refresh();
                        }
                     }, 
                     this);
    mgmtwin.show();
    srv_event_cfg = {
        run: getSrvEvent,  //执行任务时执行的函数
        interval: 7 * 1000           //任务间隔，毫秒为单位，这里是7秒
    }
    //Ext.TaskMgr.start(srv_event_cfg);//初始化时就启动任务
}
