<script setup>
import { onMounted, reactive, ref } from 'vue'
import * as echarts from 'echarts'
import { getCurrentInstance } from 'vue'
import { timestampFormat, numberFormat, copyContent } from './utils'
import { ElMessage } from 'element-plus'


function copyAddress(address) {
  if (copyContent(address)) {
    ElMessage({ message: 'Success', type: 'success', center: true })
  } else {
    ElMessage({ message: 'Failed', type: 'error', center: true })
  }
}

window.copyAddress = copyAddress;


// 用于 axios
const { proxy } = getCurrentInstance()

const nodes = ref({})
const links = ref({})
const visConfig = ref({
  node: { //节点的默认配置
    label: { //标签配置
      show: true, //是否显示
      color: '20,20,20', //字体颜色
      font: 'normal 14px Arial', //字体大小及类型 
      textPosition: 'Bottom_Center', //文字位置 Top_Center,Bottom_Center,Middle_Right,Middle_Center
      borderWidth: 0, //文字边框宽度
      borderColor: '50,50,50', //标签边框
      textOffsetY: 4, //文字偏移量
      //background:'220,220,220'//标签背景色
    },
    shape: 'circle', //rect,circle,star
    width: 64, //节点宽度
    height: 64, //节点高度
    color: '80,200,255', //节点颜色
    borderColor: '80,80,255', //边框颜色
    borderWidth: 1, //边框宽度,
    borderAlpha: 0.6, //边框透明度
    borderRadius: 5, //边框圆角大小,shape=rect时生效
    lineDash: [0], //边框虚线间隔,borderWidth>0时生效
    alpha: 1, //节点透明度
    selected: { //选中时的样式设置
      borderColor: '80,80,255', //选中时边框颜色
      borderAlpha: 0.8, //选中时的边框透明度
      borderWidth: 4, //选中时的边框宽度
      //showShadow:true,//开启阴影
      //shadowBlur:20 //阴影大小
    }
  },
  link: { //连线的默认配置
    label: { //连线标签
      show: true, //是否显示
      color: '50,50,50', //字体颜色
      font: 'normal 13px Arial', //字体大小及类型
    },
    lineType: 'direct', //连线类型,direct,curver
    colorType: 'source', //连线颜色类型 source:继承source颜色,target:继承target颜色 both:用双边颜色，defined:自定义
    alpha: 1, // 连线透明度
    showArrow: false, //显示连线箭头
  },
  wheelZoom: 0.8, //开启鼠标滚轮缩放
  highLightNeiber: false //相邻节点高亮开关
});

const visGraph = ref({})

async function initVisGraph(){
  const { data: res } = await proxy.$http.get("/txs/0x04e8cc30871649a9d941deb324d3460d6101cc57");
  const visgraph = new VisGraph(document.getElementById('vis_graph'), visConfig.value);
  visgraph.drawData(res);
  visgraph.setZoom('auto');//自动缩放

}



//1.通过vue3.x中的refs标签用法，获取到container容器实例
//html中ref了chart
const chart = ref(null);
//2.定义在本vue实例中的echarts实例
let myEcharts = ref({});
//4.定义好echarts的配置数据
let graphOption = ref({
  title: {
    text: "Dandelion",
    subtext: "author:Albert",
    top: "top",
  },
  tooltip: {
    trigger: 'item',
    animation: true,
    show: true,
    trigger: "item",
    alwaysShowContent: true,
    enterable: true,
    // triggerOn: this.settingForm.tooltipTriggerOn,
    triggerOn: "click",
    padding: 5,
    position: ['70%', '10%'],
    formatter: function (obj) {
      if (obj.dataType == 'edge') {
        const edge = obj.data
        var time = new Date(edge.st_last_tx_time)
        const time_str = time.toLocaleDateString()
        return (
          `最近交易时间:${timestampFormat(edge.st_last_tx_time)}<br>` +
          `总交易金额:${numberFormat(edge.st_total_value / 1000000)}<br>` +
          `总交易次数:${edge.st_total_num}<br>`
        );
      }

      if (obj.dataType == "node") {
        const node = obj.data
        return (
          `地址:${node.wa_address}  <button onclick="copyAddress('${node.wa_address}')">复制</button><br>`
        )
      }

    }
  },
  animationDuration: 100,
  animationEasingUpdate: "quinticInOut",
  series: [{
    label: {
      show: true,
      distance: 10,
      position: "left",
      formatter: function (obj) {
        var node = obj.data;
        return (
          `${node.name_show}`
        );
      },
    },
    edgeSymbol: ['none', 'arrow'],
    roam: true,
    symbol: 'circle',
    symbolSize: 20,
    layout: 'force',
    force: {
      repulsion: 1000,
      layoutAnimation: false
    },
    name: "USDT",
    type: "graph",
    data: [],
    links: [],
  }]
})

//onMounted钩子函数
onMounted(() => {
  //初始化echarts
  init();
  initGraph();
  // initVisGraph();
})

//初始化echarts实例方法
function init() {
  //3.初始化container容器
  myEcharts = echarts.init(chart.value);
  //5.传入数据
  myEcharts.setOption(graphOption.value);
  //additional：图表大小自适应窗口大小变化
  window.onresize = () => {
    myEcharts.resize();
  }
}
async function initGraph() {
  const { data: res } = await proxy.$http.get("/txs/0x04e8cc30871649a9d941deb324d3460d6101cc57");
  console.log(res);
  nodes.value = res.nodes
  links.value = res.links
  graphOption.value.series[0].data = nodes.value
  graphOption.value.series[0].links = links.value
  myEcharts.setOption(graphOption.value)
}

</script>


<template>
  <div class="about">
    <el-row type="center">
      <el-col :span="24">
        <el-card>
          <div id="container" ref="chart"></div>
        </el-card>
        
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
#container {
  box-sizing: border-box;
  height: 800px;
  width: 80%;
  margin: 0 auto;
}
#visGraph{
  box-sizing: border-box;
  height: 400px;
  width: 80%;
  margin: 0 auto;
}
</style>
