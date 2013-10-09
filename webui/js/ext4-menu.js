// vim: sw=4:ts=4:nu:nospell:fdc=4

createTreeNode = function(rootNode, nodeName, panelName, clickFunc){
    var node = new Ext.tree.TreeNode({
               text: nodeName,
               draggable:false,
               expanded:true,
               iconCls:"tree-node-" + panelName,
               listeners:{'click': function(){
                                var panel=Ext.getCmp(panelName);
                                if(!panel){
                                    if (panelName == 'sys-reboot' || panelName == 'sys-poweroff'){
                                       return clickFunc();
                                    }else{
                                       panel= clickFunc();
                                    }
                                }
                                main.openTab(panel);
                              }
                         }
           });
    rootNode.appendChild(node);
    return rootNode;
}

Ext.define("go.GoXiti", {
    extend: "Ext.tree.TreePanel",
    alias:  "GoXiti",
    id: "xiti_tree",
    autoScroll : false,
    animate : true,
    border : false,
    rootVisible : false,
    /*
    root: {  
        text: '树根',//节点名称  
        expanded: true,//默认展开根节点  
        children: [{  
            text: '节点一',//节点名称  
            leaf: true//true说明为叶子节点  
        }, {  
            text: '节点二',//节点名称  
            leaf: true//true说明为叶子节点  
        }]  
    }  
    */
    root : function(){
        var rootNode = new Ext.tree.TreeNode({ text: 'rootNode', draggable:false, expanded:true });
        createTreeNode(rootNode, '关于','about', null ); 
        return rootNode;
    }
});

Ext.define("go.AnalysizeXiti", {
    extend: "Ext.tree.TreePanel",
    alias:  "AnalysizeXiti",
    id: "analysize_tree",
    autoScroll: false,
    animate:true,
    border:false,
    rootVisible:false,
    root: function(){
        var rootNode = null;
        rootNode = new Ext.tree.TreeNode({ text: 'rootNode', draggable:false, expanded:true });
        createTreeNode(rootNode, '服务器重启','sys-reboot',  do_sys_reboot    ); 
        createTreeNode(rootNode, '服务器关机','sys-poweroff',do_sys_poweroff  ); 
        return rootNode;
    }
}); 

Ext.define("go.MenuPanel", {
    extend: "Ext.Panel",
    alias:  "MenuPanel",
    id : 'qmenu',
    region : 'west',
    title : "习题菜单",
    split : true,
    width : 200,
    minSize : 175,
    maxSize : 510,
    collapsible : true,
    margins : '0 0 5 5',
    cmargins : '0 0 0 0',        
    layout : "accordion",
    layoutConfig : { titleCollapse : true, animate : true },
    items : [ 
        { title : "练习", items : [new go.GoXiti ] },
        { title : "分析", items : [new go.AnalysizeXiti ] },
    ]
    
});


function reboot_handler(){
    var url = "/sysinfo?cmd=reboot_server";
    return common_ajax_handler(url);
}

function poweroff_handler(){
    var url = "/sysinfo?cmd=poweroff_server";
    return common_ajax_handler(url);
}

function shutdown_handler(title, msg, handler){
    var do_yes = function(buttonobj, inputText){
                    if(buttonobj=='yes' || buttonobj == 'ok'){
                        handler();
                    }
                 };
    show_msg(title, msg, do_yes); 
}

function do_sys_reboot(){
    return shutdown_handler('确认', '确认要重启服务器吗？', reboot_handler);
}

function do_sys_poweroff(){
    return shutdown_handler('确认', '确认要关闭服务器吗？', poweroff_handler);
}    


