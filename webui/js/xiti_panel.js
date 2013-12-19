var XITI_BASE_URL="/xmgo?item=xiti&";
var XITI_LOAD_SGF="/get_current_sgf";
var XITI_TREE_NODE_URL= XITI_BASE_URL   + "cmd=list";
var XITI_SELECT_URL= XITI_BASE_URL      + "cmd=select";
var XITI_SELECT_SGF_URL= XITI_BASE_URL  + "cmd=select_sgf";
var XITI_LOAD_SGF_URL= XITI_BASE_URL    + "cmd=load_sgf";
var XITI_SEND_INFO_URL= XITI_BASE_URL    + "cmd=send_info";
var current_xiti_set_name = ""; 
var current_select_xiti_set_name = "";
var current_xiti_number= -1;
var current_crypt = 0;
var last_flash_panel_width  = 0;
var last_flash_panel_height = 0;
var current_sgfurl ="";
var current_steps = 0;   // 走的步数
var current_trys = 0;    // 尝试的次数
var current_result = -1; // 结果：1: 成功，0：失败, -1：没有下完
var saw_demo = 0;        // 是否查看了演示，如果看了则为1，否则为0

var timer_runner = new Ext.util.TaskRunner();

Ext.ns("go");


function isRootNode(node){
    return node && node.id == '0' ? true : false;
}

function getNodeFullPath(node){
    fullpath = '';
    while(node){
        fullpath = isRootNode(node) ?    // 是根节点吗？
                   "/" + fullpath   :
                   node.text + "/" + fullpath;
        node = node.parentNode;
    }
    return fullpath;
}

function onExpandTreeNode(p, node, callback){
    ////alert('node :' + node.id  + " was double clicked!");
    var cur_dir = getNodeFullPath(node);
    var baseParams = { action:'get_xiti', dir: cur_dir, sendWhat: 'dirs'};
    this.baseParams = baseParams;
}

function switch_xiti(xiti){
    current_xiti_set_name = current_select_xiti_set_name;
    Ext.getCmp('current_xiti_set').setText( current_xiti_set_name );
    Ext.getCmp('xiti_sum').setText ( "" + xiti.sum );
    Ext.getCmp('xiti_finish_sum').setText ( "" + xiti.finish_sum );
    Ext.getCmp('current_xiti').setValue(xiti.current_num);
    on_select_xiti("current");
}

function select_xiti(node){
    if(node.isLeaf()){
        var cur_dir = getNodeFullPath(node);
        current_select_xiti_set_name = cur_dir; 
        var baseParams = { action:'select_xiti', dir: cur_dir, sendWhat: 'dirs'};
        handleCallback(baseParams, XITI_SELECT_URL, false, switch_xiti);
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

go.GoXiti = function() {
    go.GoXiti.superclass.constructor.call(this, {
    id: "xiti_tree"
    ,preloadChildren : true
    ,border  : false
    ,width   : 210 
    ,minSize : 110
    ,maxSize : 510
    ,margins : '0 0 5 5'
    ,cmargins : '0 0 0 0'        
    ,xtype: "treepanel"
    ,region: "west"
    ,closable: false
    ,titlebar: true
    ,autoScroll:true
    ,animate:true 
    ,singleClickExpand: true
    ,rootVisible: false 
    ,containerScroll: true
    ,enableDD: true
    ,ddGroup : 'TreeDD'
    ,split   : true
    //,collapsible  : true
    ,loader: new Ext.tree.TreeLoader({
                    preloadChildren: false,
                    dataUrl:XITI_TREE_NODE_URL,
                    baseParams: { action:'get_xiti', dir: '', sendWhat: 'dirs'}, // custom http params
                    listeners:  {
                            'beforeload': { fn: onExpandTreeNode }
                    }
                })
    ,root: new Ext.tree.AsyncTreeNode({
                    text: '/'
                    ,draggable:false
                    ,expanded: true
                    ,id:'0'
                    /*
                    ,listeners: {
                        'load': { fn: expandTreeToDir }
                    }
                    */
                })
    ,listeners: {"dblclick": function(node, e){
                             select_xiti(node); 
                           }
                }

  });
};
Ext.extend(go.GoXiti, Ext.tree.TreePanel);

go.FlashPanel = function() {
    go.FlashPanel.superclass.constructor.call(this, {
    id : 'flash_panel'
    ,xtype: "panel"
    //,autoScroll : true
    //,closable : false
    ,region: "center"
    ,listeners: {"afterlayout": function(){
                           load_goxiti_swf(); 
                           }
                }
  });
};
Ext.extend( go.FlashPanel, Ext.Panel );

go.MainPanel = function() {
    this.openTab = function(panel, id) {
        var o = (typeof panel == "string" ? panel : id || panel.id);
        var tab = this.getComponent(o);        
        //var tab = panel.id; 
        if (tab) {
            this.setActiveTab(tab);
        } else if(typeof panel !="string"){
            panel.id = o;
            var p = this.add(panel);
            this.setActiveTab(p);
            ///p.child('.x-tab-strip-text').highlight();
        }
    };

    this.closeTab = function(panel, id) {
        var o = (typeof panel == "string" ? panel : id || panel.id);
        var tab = this.getComponent(o);
        if (tab) {
            this.remove(tab);
            tab = null;
        }
    };

    var pass_chkbox = new Ext.form.Checkbox({ boxLabel: "跳过已完成", id: "pass_chkbox", name: "pass_chkbox", inputValue: 1 });

    var xo = new Ext.Panel({  // 必须要这样套一层panel，否则swfobject将不会显示swf flash.
                    id:"flash_wrap_panel"
                    ,xtype: 'panel'
                    ,region:'center'
                    ,layout:'fit'
                    ,items: [ new go.FlashPanel() ]
                });
    var mo = new Ext.Panel({
                    id:"xiti_panel"
                    ,title : '练习'
                    ,xtype: 'panel'
                    ,closable: false 
                    ,region:'center'
                    ,layout:'border'
                    ,header: false
                    ,tbar:[
                          '当前习题集：' 
                          ,{ id:'current_xiti_set', 
                            xtype: 'tbtext',
                            width: 260
                          }
                          ,"-"
                          ,'总数：'
                          ,{ id:'xiti_sum', 
                            xtype: 'tbtext',
                            width: 40
                          }
                          ,"-"
                          ,'完成数：'
                          ,{ id:'xiti_finish_sum', 
                            xtype: 'tbtext',
                            width: 40
                          }
                          ,"-"
                          ,{ id:'prev_xiti', 
                            iconCls:'PrevIconCss',
                            width: 80,
                            text: '上一题', 
                            handler: get_prev_xiti 
                          }
                          ,{ id:'current_xiti', 
                            xtype: 'textfield',
                            width: 40,
                            name: 'name',
                            text: '上一题', 
                            allowBlank: true
                          }
                          ,{ id:'next_xiti', 
                            iconCls:'NextIconCss',
                            width: 80,
                            text: '下一题', 
                            handler: get_next_xiti 
                          }
                          ,pass_chkbox
                          ,"->"
                          ,'状态：'
                          ,{ id:'current_xiti_status', 
                            xtype: 'tbtext',
                            width: 50
                          }
                        ]
                    ,bbar:[
                          'log：'
                          ,{ id:'msg_board', 
                            xtype: 'tbtext',
                            width: 300
                          }
                        ]
                    ,draggable:false
                    ,items: [ new go.GoXiti(), xo ]
                });
    go.MainPanel.superclass.constructor.call(this, {
     id : 'main'
    ,region : 'center'
    ,margins : '0 5 5 0'
    ,resizeTabs : true
    ,minTabWidth : 165
    ,tabWidth : 165
    ,tabHeight: 500
    ,enableTabScroll : true
    ,title : '练习'
    ,activeTab : 0
    ,listeners:{'destroy': function(panel){
                    var o = (typeof panel == "string" ? panel : id || panel.id);
                    var tab = this.getComponent(o);
                    if (tab) {
                        this.remove(tab);
                        tab = null;
                    }
                }
              }
    ,items : [ mo ]
  });
};
Ext.extend(go.MainPanel, Ext.TabPanel);

function do_load_goxiti(fp, wid, hei, url, callback){
    var attributes = { 
        id: "flash_panel"
        ,name: "xmgo"
    };
    var flashvars = {
        frame:1,
        ruler:0,
        script:1,
        crypt: current_crypt,
        sgfurl: url
    };
    var params =  {
        bgcolor: "#869ca7",
        allowScriptAccess: 'always',
        quality: 'high'
    };
    if (callback){
        swfobject.embedSWF("js/goxiti.swf", fp, ""+wid, ""+hei, "9.0.0","expressInstall.swf", flashvars, params, attributes, callback);
    }else{
        swfobject.embedSWF("js/goxiti.swf", fp, ""+wid, ""+hei, "9.0.0","expressInstall.swf", flashvars, params, attributes);
    }
    //swfobject.embedSWF("js/goxiti.swf", fp, "%100", "%100", "9.0.0","expressInstall.swf", flashvars, params, attributes);

}

function load_goxiti_swf() {
    var fp_name= "flash_panel";
    var p = Ext.getCmp(fp_name);
    var wid = p.getWidth(); 
    var hei = p.getHeight();

    if (wid < 20 || hei < 20){
        return;
    }
    /*
    if (xiti_loaded != 0){
        return;
    }
    */
    // alert("wid= " + wid  + ", hei= " + hei);
    do_load_goxiti(fp_name, wid, hei, XITI_LOAD_SGF);
    last_flash_panel_width  = wid;
    last_flash_panel_height = hei;
    xiti_loaded = 1;
}

function swfobject_callback(e){
    var o = document.getElementById("flash_panel");
    o.NewGoExercises(current_sgfurl);
}

function load_sgf(sgf_num, crypt){
    var sgfurl = XITI_LOAD_SGF_URL + "&sgf_num=" + sgf_num;
    var ext = ".sgf";
    var fp = "flash_panel";
    if (crypt && crypt == 1){
        sgfurl = sgfurl + "&crypt=1";
        ext = ".sgf_";
    }
    sgfurl = sgfurl + "&sgfurl=" + sgf_num + ext;
    current_sgfurl = sgfurl;  
    if (current_crypt != crypt){
        current_crypt = crypt;
        do_load_goxiti(fp, last_flash_panel_width, last_flash_panel_height, XITI_LOAD_SGF);
        //do_load_goxiti(fp, last_flash_panel_width, last_flash_panel_height, XITI_LOAD_SGF, swfobject_callback);
    }else{
        var o = document.getElementById(fp);
        o.NewGoExercises(sgfurl);
    }
}

function on_select_xiti(action, new_number, chkbox){
    var baseParams = { sgf_item: action };
    if (typeof(new_number) != undefined && new_number >= 0){
        baseParams.new_number = new_number;
    }
    if (typeof(chkbox) != undefined && chkbox == true){
        baseParams.pass_chk= 1;
    }else{
        baseParams.pass_chk= 0;
    }
    function select_sgf(items){
        if(typeof(items.status) != undefined && items.current_num >= 0){
            current_xiti_number = items.current_num;
            current_steps = 0;   // 走的步数
            current_trys = 0;    // 尝试的次数
            saw_demo = 0;
            Ext.getCmp('current_xiti').setValue(items.current_num);
            Ext.getCmp('xiti_finish_sum').setText ( "" + items.finish_sum );
            if (items.status == 1){
                current_result = 1; // 结果：1: 成功，0：失败， -1：没有下完
                Ext.getCmp('current_xiti_status').setText("已完成");
                Ext.get('current_xiti_status').setStyle('font-weight', 'bold');
                Ext.get('current_xiti_status').setStyle('color', 'blue');
            }else{
                current_result = 0; // 结果：1: 成功，0：失败， -1：没有下完
                Ext.getCmp('current_xiti_status').setText("未完成");
                Ext.get('current_xiti_status').setStyle('font-weight', 'bold');
                Ext.get('current_xiti_status').setStyle('color', 'red');
            }
            load_sgf(items.current_num, items.crypt);
        }
    }
    function failed_callback(arg){
        on_select_xiti("current");
    }
    if (action == 'specify'){
        // 如果指定了错误的习题号，这个回调让它恢复过来。
        handleCallback(baseParams, XITI_SELECT_SGF_URL, false, select_sgf, failed_callback);
    }else{
        handleCallback(baseParams, XITI_SELECT_SGF_URL, false, select_sgf);
    }
}

function do_backward_forward(action){
    var input_xiti_number = Ext.getCmp('current_xiti').getValue();
    if (input_xiti_number && current_xiti_number != input_xiti_number && input_xiti_number >= 0 ){
        on_select_xiti("specify", input_xiti_number);
    }else{
        if ( ! input_xiti_number ){ 
            on_select_xiti("current");
        }else{     
            var pass_chk = Ext.getCmp("pass_chkbox").getValue();
            on_select_xiti(action, -1, pass_chk);
        }
    }
}    

function get_prev_xiti(){
    send_play_info(function()  { do_backward_forward("prev"); });
}

function get_next_xiti() {
    send_play_info(function () { do_backward_forward("next"); });
}    

function get_xiti_panel() {
    var o = new go.MainPanel();
    return o;
}    

function OnUserPlayMove(x, y, color){
//棋盘落子，posX、posY为落子坐标，color为棋子颜色
   //Ext.MessageBox.alert('alert', "x=" + x + ", y=" + y );
   current_steps += 1;
}

function send_play_info(callback){
    handleCallback({ num: current_xiti_number, steps: current_steps, trys: current_trys, result: current_result, demo : saw_demo }
            , XITI_SEND_INFO_URL, false, callback);
}

function OnUserPlayResult(res){
    //解题结束，res=1：找到正解，res=0：解题错误
    current_result = res; 
    current_trys += 1;
    if (res == 1){ //如果解题成功，则直接跳到下一个题目
        func = function(arg){          
            timer_runner.stop(arg);
            get_next_xiti();
        }
        delay_call(func, 3);
    }else{
        send_play_info();
    }
}

function  OnSolutionAnimateStart(){
//开始自动演示正解图的回调消息
//   Ext.MessageBox.alert('mode', "enter exercise mode");
    //current_result = 0; 
    saw_demo = 1;
}

/*
function  OnSolutionAnimateStop(){
//
}

function  OnCommentString(strComment){
}
*/

function  delay_call(func, timeout){
    timeout = timeout * 1000;
    var task = {
        run: func,
        interval: timeout //in second
    };
    task.args = [task];
    timer_runner.start(task);
}

