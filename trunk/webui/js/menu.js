// vim: sw=4:ts=4:nu:nospell:fdc=4
Ext.ns("go");

createTreeNode = function(rootNode, nodeName, panelName, clickFunc){
    var node = new Ext.tree.TreeNode({
               text: nodeName,
               draggable:false,
               expanded:true,
               iconCls:"tree-node-" + panelName,
               listeners:{'click': function(){
                                var panel=Ext.getCmp(panelName);
                                if(!panel && clickFunc ){
                                   panel= clickFunc();
                                }
                                main.openTab(panel);
                              }
                         }
               });
    rootNode.appendChild(node);
    return rootNode;
}

go.PracticeXiti = function() {
    create_root = function(){
        var rootNode = new Ext.tree.TreeNode({ text: 'rootNode', draggable:false, expanded:true });
        createTreeNode(rootNode, '全部题目','about', null ); 
        createTreeNode(rootNode, '作业','about', null ); 
        return rootNode;
    };
    root_node = create_root();
    go.PracticeXiti.superclass.constructor.call(this, {
        id: "practice_xiti_tree"
        ,preloadChildren : true
        ,autoScroll : false
        ,animate : true
        ,border : false
        ,rootVisible : false
        ,root : root_node
    });
};
Ext.extend(go.PracticeXiti, Ext.tree.TreePanel);

go.AnalysizeXiti = function() {
    create_root = function(){
        var rootNode = null;
        rootNode = new Ext.tree.TreeNode({ text: 'rootNode', draggable:false, expanded:true });
        createTreeNode(rootNode, '统计','StatPanel', function() { return new go.StatPanel();}); 
        return rootNode;
    };
    root_node = create_root();
    go.AnalysizeXiti.superclass.constructor.call(this, {
        id: "analysize_tree"
        ,autoScroll: false
        ,animate:true
        ,border:false
        ,rootVisible:false
        ,root: root_node
  }); 
};
Ext.extend(go.AnalysizeXiti, Ext.tree.TreePanel);

go.MenuPanel = function() {
    go.MenuPanel.superclass.constructor.call(this, {
    id : 'qmenu',
    region : 'west',
    title : "菜单",
    split : true,
    width : 110,
    minSize : 110,
    maxSize : 510,
    collapsible : true,
    margins : '0 0 5 5',
    cmargins : '0 0 0 0',        
    autoScroll:false,
    layout : "accordion",
    layoutConfig : { titleCollapse : true, animate : true },
    items : [ 
        { title : "练习", items : [new go.PracticeXiti ] },
        { title : "分析", items : [new go.AnalysizeXiti ] }
    ]
  });
};
Ext.extend(go.MenuPanel, Ext.Panel);

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

function do_stat(){
///    return shutdown_handler('确认', '确认要关闭服务器吗？', poweroff_handler);
}    


