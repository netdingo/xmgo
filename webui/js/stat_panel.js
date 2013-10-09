// vim: sw=4:ts=4:nu:nospell:fdc=4
Ext.chart.Chart.CHART_URL = '/ext/resources/charts.swf';  
Ext.ns("go");

var xitiStore = new Ext.data.JsonStore({
    root:'',
    id:'resourceid',
    remoteSort: false,
    pruneModifiedRecords:true, //设置为true,则每次当store装载或有record被移除时,清空所有修改了的record信息. 默认为false.
    fields: [ //两对键值对，这是name
        'resourceid',
        {name:'contentno', mapping:'content.contentno'},
    ],
    proxy: new Ext.data.HttpProxy({
        url: 'operation/resource/manageresource.jsp'//相对路径
    })
});

 
go.StatPanel= function(){
    go.GoXiti.superclass.constructor.call(this, {
        id : 'StatPanel'
        ,closable: true
        ,autoScroll:true
        ,title : '统计信息'
        ,frame : true
        //,layout:'border'
        //,region:'center'
        //,autoLoad :"sysinfo?cmd=query"
        ,refresh:function(){
          //
        }
        ,listeners: {     //Panel添加LoadMask
            'afterrender': function(comp) {
                //new Ext.LoadMask(comp.getEl(), { store: xitiStore });    //当xitiStore加载时在Panel上显示Mask
            }
        }
        ,items: [{    //Column Bar Chart子组件
            xtype: 'chart',    //chart xtype
            store: xitiStore,    //Store of data
            listeners: {    //柱状图数据刷新以后，如果有数据存在，则默认执行点击第一个柱的操作（高亮显示选中的柱）
                'refresh': function(chart) {
                    var items = chart.series.get(0).items, i;    //series为图标的数据组，本例中只显示一组柱状图，所以取get(0)的items数据对象
                    for(i = 0; i < items.length; i++) {
                        //通过storeItem对象回去xField或者yField轴对应的数据，示例中为找到并选中第一个不等于0的横坐标点
                        if(items[i].storeItem.get('data') != 0) {
                            setTimeout(_selectMonthItem(items[i]), 600);    //延迟600ms执行
                            break;
                        }
                    }
                }
            },
            axes: [{    //定义坐标轴
                type: 'Numeric',    //坐标轴数据类型为数据
                position: 'left',    //左侧、纵坐标
                fields: 'data',    //该坐标轴对应设置的xitiStore中的某个Field
                label: {    //格式化坐标轴上刻度数据显示
                    //renderer: Ext.util.Format.numberRenderer('0')    //格式化为整数
                },
                title: 'Energy(KWh)',    //坐标轴名称
                grid: true,    //是否在图表上显示横向网格
                minimum: 0    //纵坐标最小值，最大值对应为maximum
            }, {
                type: 'Category',    //坐标轴类型
                position: 'bottom',    //表示为横坐标
                fields: 'name',    //对应xitiStore中的Field
                title: false    //不显示坐标轴名称
            }],
            series: [{    //数据，一个series子项表示一组可展示的数据（曲线图为一条曲线，柱状图为一组柱子。。）
                type: 'column',    //表示该组数据以柱状图方式显示
                axis: 'left',    //绑定数据对应的坐标轴，默认值为"left"，如果绑定bottom，则显示为横向的柱状图
                style: {    //柱子显示样式
                    opacity: 0.85,    //透明度
                    fill: '#8CC81E'    //填充颜色
                },
                highlightCfg: {    //该配置参数API文档中没有说明，不过官方例子里有，为高亮状态的样式
                    opacity: 0.85,    //透明度
                    fill: '#f0fea5'    //填充颜色
                },
                label: {    //柱子上数值的显示样式，具体属性可参考API
                    display: 'insideEnd',    //表明Label显示的位置
                    'text-anchor': 'middle',    //对齐方案
                    field: 'data',    //the name of field to displayed in the label, default value: 'name'
                    //renderer: labelRender,    //显示Label的格式化函数
                    orientation: 'horizontal',    //水平显示
                    color: '#333'    //Label颜色
                },
                listeners: {    //为柱状图添加click事件，没有专门的click事件，使用mouseup替代
                    'itemmouseup': function(item) {
                        //selectMonthItem(item);    //处理选中某一个Item的自定义函数
                    }
                },
                xField: 'name',    //xField
                yField: 'data'    //yField
            }]
        }]
    });
}
Ext.extend(go.StatPanel, Ext.Panel);

 
function selectMonthItem(item) {    //处理选中某一个Item的自定义函数
    /*
    var series = monthHistogram.down('chart').series.get(0);    //获取series
 
    series.highlight = true;    //指定highlight属性为true，该属性为false时好像无法设置、取消高亮，记不清了~~
    series.unHighlightItem();    //取消所有高亮状态Item的高亮状态
    series.cleanHighlights();    //API上没看到，不过官方例子里有
    selectedMonthStoreItem = item.storeItem;
    series.highlightItem(item);    //highlightItem方法接收storeItem属性
    series.highlight = false;    //如果不将该属性关闭，则鼠标移动到柱子上时即时不点击也会高亮显示
 
    setTimeout(loadDayData, 200);    //200ms后重新加载在月柱状图中选中的日期当天的功率曲线图
    */
}
 
function _selectMonthItem(item) {    //让setTimeout方法对应的函数可以传递参数
    /*
    return function() {
        selectMonthItem(item);
    };
    */
}
 
function loadMonthData() {    //刷新示例柱状图数据的方法，重新加载chart指定的store即可自动刷新
    /*
    xitiStore.load({
        params: {    //HTTP请求中要传递的参数
            param: 'month',
            nodeId: getCurrentNodeId(),
            month: selectedYearStoreItem.get('name')
        }
    });
    */
}
