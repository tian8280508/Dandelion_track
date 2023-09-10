<template>
  <div class="about">
    <el-row type="center" :gutter="5">
      <!-- 左边部分 -->
      <el-col :span="10">

        <!-- 左上 -->
        <el-card style="height: 500px;">
          <el-table :data="showAddressesTable" style="width: 100%" v-if="currentClick == 'classNode'"
            :max-height="tableMaxHeight">
            <el-table-column prop="address" label="地址" sortable />
          </el-table>

          <el-table :data="nodeStTable" style="width: 100%" v-if="currentClick == 'node'" :max-height="tableMaxHeight">
            <el-table-column prop="st_from" label="头节点" sortable :show-overflow-tooltip='true' min-width="40" />
            <el-table-column prop="st_to" label="尾节点" sortable :show-overflow-tooltip='true' min-width="40" />
            <el-table-column prop="st_total_num" label="总笔数" sortable min-width="40" />
            <el-table-column prop="st_total_value" label="总金额" sortable min-width="40" />
            <el-table-column prop="st_last_tx_time" label="最近时间" sortable min-width="60"
              :show-overflow-tooltip='true' />
          </el-table>
          <el-table :data="txTable" style="width: 100%" v-if="currentClick == 'linkBetweenNodes'"
            :max-height="tableMaxHeight">
            <el-table-column prop="tx_id" label="hash" sortable min-width="40" :show-overflow-tooltip='true' />
            <el-table-column prop="tx_from" label="头节点" sortable :show-overflow-tooltip='true' min-width="40" />
            <el-table-column prop="tx_to" label="尾节点" sortable :show-overflow-tooltip='true' min-width="40" />
            <el-table-column prop="tx_value" label="金额" sortable min-width="40" />
            <el-table-column prop="tx_time" label="时间" sortable min-width="60" />
          </el-table>

        </el-card>
        <!-- 左下 ctrl k -->
        <el-card>
          <el-tabs v-model="activeTab" class="demo-tabs" @tab-click="handleClick">

            <el-tab-pane label="节点导入 | 交易过滤" name="importNodeTab">
              <el-scrollbar :height="scrollbarHeight">
                <el-form :model="txFilterForm" label-position="left" label-width="120px" style="max-width: 400px">
                  <el-form-item label="起时间">
                    <el-date-picker class="rectangleItem" v-model='txFilterForm.start_time' type="date"
                      format="YYYY/MM/DD" value-format="YYYY-MM-DD" :default-value="new Date(2019, 10, 9)" />
                  </el-form-item>
                  <el-form-item label="止时间">
                    <el-date-picker class="rectangleItem" v-model='txFilterForm.end_time' type="date"
                      format="YYYY/MM/DD" value-format="YYYY-MM-DD" :default-value="new Date(2023, 10, 0)" />
                  </el-form-item>

                  <el-form-item label="金额基数">
                    <el-input class="rectangleItem" v-model="txFilterForm.value_threshold" clearable>
                      <template #prefix>
                        <el-icon class="el-input__icon">
                          <Filter />
                        </el-icon>
                      </template>
                    </el-input>
                  </el-form-item>


                  <el-form-item label="扩展类型">
                    <el-select class="rectangleItem" clearable>
                      <template #prefix>
                        <el-icon class="el-select__icon">
                          <DataLine />
                        </el-icon>
                      </template>
                    </el-select>
                  </el-form-item>

                  <el-form-item label="扩展层数">
                    <el-select class="rectangleItem" clearable>
                      <template #prefix>
                        <el-icon class="el-select__icon">
                          <DCaret />
                        </el-icon>
                      </template>
                    </el-select>
                  </el-form-item>


                  <el-form-item label="交易数量限制">
                    <el-input class="rectangleItem" v-model="txFilterForm.st_num_limit" clearable>
                      <template #prefix>
                        <el-icon class="el-input__icon">
                          <Filter />
                        </el-icon>
                      </template>
                    </el-input>
                  </el-form-item>
                  <el-divider content-position="left">交易过滤</el-divider>

                  <el-form-item label="导入节点">
                    <el-input style=" width: 260px;" placeholder="请输入单节点的地址" v-model="importAddress" clearable>
                      <template #append>
                        <el-button @click="addNodeDraw">
                          <el-icon>
                            <UploadFilled />
                          </el-icon>
                        </el-button>
                      </template>
                    </el-input>
                  </el-form-item>
                </el-form>

              </el-scrollbar>

            </el-tab-pane>
            <el-tab-pane label="群组导入 | 类过滤" name="importGroupTab">
              <el-scrollbar :height="scrollbarHeight">
                <el-form :model="classFilterForm" label-position="left" label-width="120px" style="max-width: 400px">
                  <el-form-item label="聚类基数">
                    <el-input class="rectangleItem" v-model="classFilterForm.class_num" clearable>
                      <template #prefix>
                        <el-icon class="el-input__icon">
                          <Filter />
                        </el-icon>
                      </template>
                    </el-input>
                  </el-form-item>

                  <el-form-item label="入度限制">
                    <el-input class="rectangleItem" v-model="classFilterForm.in_degree" clearable>
                      <template #prefix>
                        <el-icon class="el-input__icon">
                          <Filter />
                        </el-icon>
                      </template>
                    </el-input>
                  </el-form-item>

                  <el-form-item label="出度限制">
                    <el-input class="rectangleItem" v-model="classFilterForm.out_degree" clearable>
                      <template #prefix>
                        <el-icon class="el-input__icon">
                          <Filter />
                        </el-icon>
                      </template>
                    </el-input>
                  </el-form-item>
                  <el-form-item label="最大度限制">
                    <el-input class="rectangleItem" v-model="classFilterForm.max_degree" clearable>
                      <template #prefix>
                        <el-icon class="el-input__icon">
                          <Filter />
                        </el-icon>
                      </template>
                    </el-input>
                  </el-form-item>

                  <el-form-item label="度限制">
                    <el-input class="rectangleItem" v-model="classFilterForm.degree_sum" clearable>
                      <template #prefix>
                        <el-icon class="el-input__icon">
                          <Filter />
                        </el-icon>
                      </template>
                    </el-input>
                  </el-form-item>
                  <el-divider content-position="left">类过滤</el-divider>

                  <el-form-item label="节点群组">
                    <el-tag v-for="address in groupAddresses" :key="address" class="mx-1" closable
                      :disable-transitions="false" @close="handleAddrTagClose(address)">
                      {{ address.substring(0, 18) }}...
                    </el-tag>
                    <el-input v-if="inputVisible" ref="saveTagInput" v-model="inputAddressTagValue"
                      class="input-new-tag" size="small" @keyup.enter="handleInputConfirm" @blur="handleInputConfirm" />
                    <el-button v-else class="button-new-tag" size="small" @click="showTagInput">
                      + 添加地址
                    </el-button>

                    <el-button @click="addGroupDraw" type="info" size="small">
                      <el-icon>
                        <UploadFilled />
                      </el-icon>
                    </el-button>
                  </el-form-item>

                  <el-row type="flex" justify="end">
                    <el-col :span="10">

                    </el-col>
                  </el-row>




                </el-form>

              </el-scrollbar>

            </el-tab-pane>
            <el-tab-pane label="布局配置" name="visLayoutConfTab">
              <el-scrollbar :height="scrollbarHeight">
                <div v-if="visLayoutConf">
                  <el-form label-position="left" label-width="80px" :inline="true">
                    <el-form-item label="切换布局">
                      <el-select class="rectangleItem" v-model="visLayoutSelect" @change="visLayoutSelectChange">
                        <el-option v-for="(visLayoutName, index) in visLayoutOption" :key="index" :label="visLayoutName"
                          :value="visLayoutName"></el-option>
                      </el-select>
                    </el-form-item>

                    <el-form-item>
                      <el-button type="primary" v-on:click="resetVisLayoutConf">重置布局设置</el-button>

                    </el-form-item>

                  </el-form>
                  <el-divider content-position="left">布局配置</el-divider>
                  <el-form :model="visLayoutConfForm" label-position="left" label-width="80px">
                    <el-form-item v-for="(config, index) in visLayoutConf" :label="config.label" :key="index">
                      <div v-for="(value, key, index2) in config" :key="index2">
                        <!-- 不是label 标签 并且值不是数组 说明是数字 -->
                        <el-input class="rectangleItem"
                          v-if="Array.isArray(visLayoutConf[index][key]) == false && key != 'label'"
                          v-model="visLayoutConfForm[key]" :placeholder="value"></el-input>
                        <el-select class="rectangleItem" v-if="Array.isArray(visLayoutConf[index][key]) == true"
                          placeholder="Select" v-model="visLayoutConfForm[key]">
                          <el-option v-for="item in value" :key="item.value" :label="item.label" :value="item.value" />
                        </el-select>
                      </div>
                    </el-form-item>

                    <div class="formButton">
                    </div>



                  </el-form>
                </div>

                <div v-else>无布局</div>
              </el-scrollbar>

            </el-tab-pane>
            <el-tab-pane label="APIKEY" name="apiKeyTab">
              <el-form label-position="left" label-width="120px">
                <el-form-item label="apikey">
                  <el-input style=" width: 260px;" placeholder="请输入apikey" v-model="apikey">
                    <template #append>
                      <el-button @click="updateApikey">
                        <el-icon>
                          <upload />
                        </el-icon>
                      </el-button>
                    </template>
                  </el-input>
                </el-form-item>
              </el-form>
            </el-tab-pane>
            <el-tab-pane label="元素自定义" name="elementConfTab">

              <el-form label-position="left" label-width="120px"
                v-if="currentClick == 'node' || currentClick == 'classNode'" :model="nodeConfForm">
                <el-form-item label="是否显示标签">
                  <el-switch v-model="nodeConfForm.showlabel" />
                </el-form-item>
                <el-form-item label="节点标签">
                  <el-input style=" width: 260px;" placeholder="请输入节点标签" v-model="nodeConfForm.label" clearable>
                  </el-input>
                </el-form-item>
                <el-form-item label="节点大小">
                  <el-input style=" width: 260px;" placeholder="请输入节点大小" v-model="nodeConfForm.radius" clearable>
                  </el-input>
                </el-form-item>
                <el-form-item label="节点透明度">
                  <el-input style=" width: 260px;" placeholder="请输入节点透明度" v-model="nodeConfForm.alpha" clearable>
                  </el-input>
                </el-form-item>
                <el-form-item label="节点颜色">
                  <el-input style=" width: 260px;" placeholder="请输入节点颜色" v-model="nodeConfForm.fillColor" clearable>
                  </el-input>
                </el-form-item>
                <el-form-item>
                  <el-button @click="changeNodeConf">更改节点配置</el-button>
                </el-form-item>


              </el-form>
            </el-tab-pane>
            <el-tab-pane label="社群发现配置" name="communityConfTab">
              <el-form label-position="left" label-width="120px">
              </el-form>
            </el-tab-pane>
          </el-tabs>

        </el-card>


      </el-col>
      <!-- 右边部分 -->
      <el-col :span="14">
        <el-card>

          <!-- 画布上的工具栏 -->
          <el-row>
            <el-col :span="8">
              <el-button @click="backout" type="danger">
                撤销
              </el-button>
              <el-button @click="saveData2Local" type="primary">
                保存
              </el-button>


              <el-popconfirm title="现有的节点,本地保存的记录都将不见" @confirm="clearGraph">
                <template #reference>
                  <el-button type="success">
                    清除
                  </el-button>
                </template>
              </el-popconfirm>

              <!-- <el-button circle type="warning" @click="">
                <el-icon>
                  <Printer />
                </el-icon>
              </el-button> -->

              <el-button circle plain @click="relocationGraph">
                <el-icon>
                  <Aim />
                </el-icon>
              </el-button>
              <!-- 
              <el-button circle plain @click="graphZoomOut">
                <el-icon>
                  <Aim />
                </el-icon>
              </el-button>
              <el-button circle plain @click="graphZoomIn">
                <el-icon>
                  <Aim />
                </el-icon>
              </el-button> -->

            </el-col>
            <el-col :span="8">
              <el-input style="width: 250px;" placeholder="请输入需要查找节点的地址" v-model="searchAddress">
                <template #append>
                  <el-button @click="searchNode">
                    <el-icon>
                      <search />
                    </el-icon>
                  </el-button>
                </template>
              </el-input>

            </el-col>
            <el-col :span="8">

              <el-input style=" width: 260px;" placeholder="请输入需添加节点的地址" v-model="importAddress" clearable>
                <template #append>
                  <el-button @click="addNodeDraw">
                    <el-icon>
                      <UploadFilled />
                    </el-icon>
                  </el-button>
                </template>
              </el-input>
            </el-col>
          </el-row>
          <div id="container" ref="chart"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { toRaw } from '@vue/reactivity'
import { timestampFormat, numberFormat, copyContent, randomNum, objValueStr2Num, deepClone } from './utils'
import { ElMessage } from 'element-plus'
import { visConf } from './assets/visConf.js'
import { runXXLayout } from './assets/visLayout'
import { Delete, Edit, Search, Share, Upload, DocumentCopy, Plus, Filter, UploadFilled, Picture, Printer, Aim, ZoomOut, DCaret, DataLine } from '@element-plus/icons-vue'

var visgraph = null
var headers = {
  headers: { 'Content-Type': 'application/json; charset=utf-8' }
}
export default {
  components: {
    Delete, Edit, Search, Share, Upload, DocumentCopy, Plus, Filter, UploadFilled, Picture, Printer, Aim, DCaret, DataLine
  },
  mounted() {
    this.initVisGraph()
  },

  data() {//为组件注册数据
    return {
      nodeConfForm: {
        label: 'test',
        showlabel: true,
        radius: 1,
        fillColor: 'test',
        alpha: 1
      },
      nodeConf: ['label', 'showlabel', 'radius', 'fillColor', 'alpha'],
      elementConfForm: {},// 元素自定义
      searchState: false,// 是否是查找高亮
      txTable: [],
      tableMaxHeight: 470,
      // scrollbarHeight: '275px',
      scrollbarHeight: 600,
      nodeStTable: [],
      currentClickOption: ['node', 'classNode', 'linkBetweenNodes'],
      currentClick: "linkBetweenNodes", // 判断现在点击的节点类型
      showAddressesTable: [],// 对于class来说需要展示的列表
      inputVisible: false,
      inputAddressTagValue: '',//输入的地址标签的值 
      // groupAddresses: [
      //   '0x189df2a9e40ae85c76bf821d07137a7d2f8fe279',
      //   '0x5091290dea577fd1890edd1c47bfc962119c7d50',
      //   '0x7f6f62e9fe27bf3876087db88c652e20c382c9af',
      //   '0x95d11184b9bbfb57bf2712a5966494e886f0ec9d'
      // ],
      // groupAddresses: [
      //   '0x04e8cc30871649a9d941deb324d3460d6101cc57',
      //   '0xc890d861b3cf456be410503b2120ff3b2965347c',
      //   '0xcbf11fed85aaa5377a1268ae84b3f3692ef98da4'
      // ],
      groupAddresses: ['0x957EbB248503336d8c2E0DF0D9Ac4AbEaCcF3327', '0x3f305417ddc1771dbff8da29cfc20d5331b488da'],
      classFilterForm: {
        class_num: 1,
        in_degree: 0,
        out_degree: 0,
        max_degree: 0,
        degree_sum: 0
      },//类过滤
      searchAddress: '0x189df2a9e40ae85c76bf821d07137a7d2f8fe279',
      dataStep: {
        importAddresses: [],
        data: []
      }, // 每次读取数据的时候,记录importAddress和获取的res都会push 进去，然后删除的时候会pop 出来
      txFilterForm: {
        start_time: "1971-10-9",
        end_time: '2037-10-9',
        value_threshold: 0,
        st_num_limit: 10000,
      }, // 交易过滤表
      apikey: 'YnOUlgesgKP2wTTQm04Z',
      importAddress: '0x04e8cc30871649a9d941deb324d3460d6101cc57',// 绑定的需要提交的节点
      activeTab: "elementConfTab", //激活的tab
      visLayoutOption: ["Tree", "Kk", "FastFR", "Radiatree", "FrDirect", 'Concentric', 'Hubsize'],// 可选布局
      visLayoutSelect: '',//选中的布局
      visLayoutConfForm: {},//布局设置表单绑定
      existLayoutName: '', //现有布局的名称
      visConf, // 设置文件传入
      visLayoutConf: null, // 布局设置
      if_layout: false,// 判断节点是否布局了
    }
  },
  methods: {
    // ctrl k 4
    // --------------------------挂载在mount上的函数---------------------
    initVisGraph() {
      // 重写函数
      const that = this
      this.visConf.node.onClick = function (event, node) {
        that.getClassNodeAddresses(node)
        that.getNodeSts(node)
        that.getNodeConf(node)
        console.log(that.nodeConfForm);
      }
      this.visConf.node.ondblClick = function (event, node) {
        that.expandAndContractNode(node)
        that.copyNodeAddress(node)
      }
      this.visConf.node.onMouseOver = function (event, node) {
        if (!that.searchState) {
          visgraph.highLightNeiberNodes(node, 0.5)
        }
      }
      this.visConf.node.onMouseOut = function (event, node) {
        if (!that.searchState) {
          visgraph.restoreHightLight()
        }
      }
      this.visConf.noElementClick = function (event, node) {
        that.searchState = false
        visgraph.restoreHightLight()
      }

      this.visConf.link.onClick = function (event, link) {
        that.getLinkTxs(link)
      }
      visgraph = new VisGraph(document.getElementById('container'), this.visConf);
      const dataStepNew = JSON.parse(window.localStorage.getItem('visgraphData'))
      if (dataStepNew) {
        this.dataStep = dataStepNew // 继承dataStep
        this.addAccDataStep()
      }
    },
    // --------------------------挂载在mount上的函数---------------------


    // ----------------------------tag相关------------------------------
    showTagInput() {
      this.inputVisible = true;
      this.$nextTick(_ => {
        this.$refs.saveTagInput.$refs.input.focus();
      });
    },

    handleAddrTagClose(tag) {
      this.groupAddresses.splice(this.groupAddresses.indexOf(tag), 1)
    },

    handleInputConfirm() {
      let inputAddressTagValue = this.inputAddressTagValue;
      if ((inputAddressTagValue)) {
        console.log(this.groupAddresses.length);
        if (this.groupAddresses.length < 6) {
          this.groupAddresses.push(inputAddressTagValue);

        } else {
          ElMessage({
            message: '节点数不能超过6',
            type: 'error'
          })
        }
      }

      this.inputVisible = false;
      this.inputAddressTagValue = '';
    },
    // ----------------------------tag相关------------------------------



    // ------------------------------上方工具栏----------------------------
    // 放大
    graphZoomOut() {
      visgraph.setZoom('ZoomOut')
    },
    graphZoomIn() {
      visgraph.setZoom('ZoomIn')
    },
    //保存图片
    savePic() {
      visgraph.saveImage()
    },
    // 查找节点
    searchNode() {
      const nodes = visgraph.nodes
      for (let i = 0; i < nodes.length; i++) {
        let node = nodes[i]
        if (node.properties.address == this.searchAddress) {
          this.searchState = true
          visgraph.highLightNeiberNodes(node)
          return node
        }
      }
      ElMessage({ message: '未找到该地址信息！', type: 'error' })
    },
    // 根据dataStep 添加节点 工具函数
    addAccDataStep() {
      for (let i = 0; i < this.dataStep.data.length; i++) {
        const res = this.dataStep.data[i]
        visgraph.activeAddNodeLinks(res.nodes, res.links)
        this.visLayoutConf = runXXLayout("Tree", visgraph.getGraphData()).getConfig();
        this.existLayoutName = "Tree"
        this.visLayoutSelect = "Tree"
        this.drawClassNode()
      }
    },
    // 清空图，dataStep, 本地存储
    clearGraph() {
      visgraph.clearAll()
      this.dataStep = {
        importAddresses: [],
        data: []
      }
      localStorage.clear();
      ElMessage({
        message: '彻底干净了'
      })
    },
    // 保存
    saveData2Local() {
      var visgraphData = visgraph.getGraphData()
      localStorage.setItem("visgraphData", JSON.stringify(this.dataStep))
      ElMessage({
        message: `保存成功！共${this.dataStep.data.length}个查询结果`,
        type: 'success'
      })
    },
    // 撤销
    backout() {
      if (this.dataStep.importAddresses.length == 0) {
        ElMessage({
          type: 'error',
          message: '无可撤销操作'
        })
        return
      }
      visgraph.clearAll()
      this.dataStep.importAddresses.pop()
      this.dataStep.data.pop()
      this.addAccDataStep()
      this.drawClassNode()
      visgraph.setZoom('auto')
      ElMessage({
        message: `撤销成功`,
        type: 'success',
      })
    },

    relocationGraph() {
      visgraph.setZoom('auto')
    },
    // ------------------------------上方工具栏----------------------------



    // ------------------------点击事件-----------------------------
    // 获取普通节点之间的交易记录
    async getLinkTxs(link) {
      if ((link.source.properties.address != undefined) & (link.target.properties.address != undefined)) {
        const { data: res } = await this.$http.post(`/tx`, {
          source_address: link.source.properties.address,
          target_address: link.target.properties.address,
        }, headers)

        for (let i = 0; i < res.txs.length; i++) {
          res.txs[i].tx_time = timestampFormat(res.txs[i].tx_time)
        }
        this.txTable = res.txs
        this.currentClick = this.currentClickOption[2]
      }
    },
    // 展开节点 收拢节点
    expandAndContractNode(node) {
      console.log(node);
      visgraph.selectRelate(node)
      const nodes = visgraph.nodes
      if (node.tipText) {
        for (let i = 0; i < visgraph.nodes.length; i++) {
          if (nodes[i].selected == true) {
            nodes[i].visible = true
          }
        }
        node.tipText = null
      } else {
        var count = 0
        for (let i = 0; i < visgraph.nodes.length; i++) {
          if ((nodes[i].selected == true) & (nodes[i] != node)) {
            if ((nodes[i].inLinks.length + nodes[i].outLinks.length) == 1) {
              count++
              nodes[i].visible = false
            }
          }
        }
        if (count > 0) {
          node.tipText = count
        }
      }
    },
    // 获取class节点类用于展示
    getClassNodeAddresses(node) {
      this.showAddressesTable = []
      if (node.properties.class == true) {
        // 聚类节点
        for (let i = 0; i < node.properties.addresses.length; i++)
          this.showAddressesTable.push({
            address: node.properties.addresses[i]
          })
        this.currentClick = this.currentClickOption[1]
      } else {
        console.log('普通节点');
      }
    },
    // 复制节点地址
    copyNodeAddress(node) {
      if (node.properties.address) {
        copyContent(node.properties.address)
        this.importAddress = node.properties.address
        ElMessage({
          message: `地址已经复制到剪贴板${node.properties.address}和导入节点处`,
          type: 'success',
        })
      }
    },
    // 请求该普通节点的交易统计信息
    async getNodeSts(node) {
      if (node.properties.address) {
        const { data: res } = await this.$http.get(`/st/${node.properties.address}`)
        for (let i = 0; i < res.sts.length; i++) {
          res.sts[i].st_last_tx_time = timestampFormat(res.sts[i].st_last_tx_time)
        }
        this.nodeStTable = res.sts
        this.currentClick = this.currentClickOption[0]
      }
    },
    // 获取节点信息
    getNodeConf(node) {
      this.nodeConfForm = {
        node: node,
        label: node.label,
        showlabel: node.showlabel,
        radius: node.radius,
        fillColor: node.fillColor,
        alpha: node.alpha
      }
      console.log(this.nodeConfForm);
    },

    // ------------------------点击事件-----------------------------




    // ------------------------表单----------------------------
    // 布局选项变更
    visLayoutSelectChange(val) {
      this.visLayoutConf = runXXLayout(val, visgraph.getGraphData(), this.visLayoutConfForm).getConfig();
      this.existLayoutName = val
      this.visLayoutSelect = val // 更改选中的布局的值
      visgraph.setZoom('auto');//自动缩放
    },
    // 布局参数变更
    resetVisLayoutConf() {
      runXXLayout(this.existLayoutName, visgraph.getGraphData(), this.visLayoutConfForm);
      this.drawClassNode()
      visgraph.setZoom('auto');//自动缩放
    },

    //更改节点配置
    changeNodeConf() {
      console.log(this.nodeConfForm);
      this.nodeConfForm.node.label = this.nodeConfForm.label
      this.nodeConfForm.node.showlabel = this.nodeConfForm.showlabel
      this.nodeConfForm.node.radius = this.nodeConfForm.radius
      this.nodeConfForm.node.fillColor = this.nodeConfForm.fillColor
      this.nodeConfForm.node.alpha = this.nodeConfForm.alpha
    },
    // ------------------------表单----------------------------



    //-------------------------------数据获取----------------------------
    // 更改聚类节点的配置 工具函数
    drawClassNode() {
      // 重新渲染节点和边的函数
      const nodes = visgraph.nodes;
      for (let i = 0; i < nodes.length; i++) {
        if (nodes[i].properties.class) {// 说明是聚类节点
          nodes[i].showlabel = false
          nodes[i].alpha = 0.5
          nodes[i].radius = 5 + nodes[i].properties.addresses.length / 5  // 根据聚类数量调整大小
        }
      }
      const links = visgraph.links;
      for (let i = 0; i < links.length; i++) {
        if (links[i].properties.total_num) {// 说明是连接普通节点的边
          if (links[i].properties.total_num > 50) {
            console.log(links[i].properties.total_value);
            const strNum = numberFormat(links[i].properties.total_value, 2)
            links[i].label = `${links[i].properties.total_num}笔，共${strNum}`
            links[i].showlabel = true

            links[i].lineWidth = 8
          } else {
            links[i].lineWidth = 3 + links[i].properties.total_num / 10 // 根据聚类数量调整大小
          }

        }
      }
    },
    // 添加单节点 从this.importAddress中读数据 不需要参数
    async addNodeDraw() {
      ElMessage({
        message: `节点${this.importAddress}正在加载`,
        type: 'success',
      })
      // 最先构建图，而不是等数据获取到了再画图 因此把构建图放在mount中
      const { data: res } = await this.$http.post(`/graph/${this.importAddress}`, {
        tx_filter: this.txFilterForm
      }, {
        headers: { 'Content-Type': 'application/json; charset=utf-8' }
      });

      visgraph.activeAddNodeLinks(res.nodes, res.links)
      this.dataStep.importAddresses.push(toRaw(this.importAddress))
      this.dataStep.data.push(res)
      this.drawClassNode()
      this.visLayoutConf = runXXLayout("FastFR", visgraph.getGraphData()).getConfig();
      this.existLayoutName = "FastFR"
      this.visLayoutSelect = "FastFR"
      visgraph.setZoom('auto');//自动缩放
      ElMessage({
        message: `节点${this.importAddress}加载成功`,
        type: 'success',
      })
    },
    // 更新apikey
    async updateApikey() {
      console.log(this.apikey);
      const { data: res } = await this.$http.post(`/api/update`, {
        apikey: this.apikey
      }, {
        headers: { 'Content-Type': 'application/json; charset=utf-8' }
      })
      if (res.status == '200') {
        ElMessage({
          message: `apikey更改成功,当前apikey为${this.apikey}`,
          type: 'success',
        })
      }
    },
    // 提交节点群
    async addGroupDraw() {
      if (this.groupAddresses.length < 2) {
        ElMessage({
          message: `至少提交两个地址`,
          type: 'error',
        })
        return
      }

      ElMessage({
        message: `节点群正在加载`,
        type: 'success',
      })
      // 最先构建图，而不是等数据获取到了再画图 因此把构建图放在mount中
      const { data: res } = await this.$http.post(`/graph/group`, {
        class_filter: this.classFilterForm,
        group_addresses: this.groupAddresses
      }, {
        headers: { 'Content-Type': 'application/json; charset=utf-8' }
      });
      visgraph.activeAddNodeLinks(res.nodes, res.links)
      this.dataStep.importAddresses.push(toRaw(this.groupAddresses))
      this.dataStep.data.push(res)
      this.visLayoutConf = runXXLayout("Tree", visgraph.getGraphData()).getConfig();
      this.existLayoutName = "Tree"
      this.visLayoutSelect = "Tree"
      this.drawClassNode()
      visgraph.setZoom('auto');//自动缩放
      // visgraph.clearClusters();//清空原有分组
      //创建社群发现算法
      // var cluster = new ClusterFactory(visgraph.getGraphData()).createClutser('louvain');
      // cluster.applay();
      ElMessage({
        message: `节点群加载成功`,
        type: 'success',
      })
    },
    //-------------------------------数据获取----------------------------

  },
}
</script>

<style scoped>
.el-tag {
  width: 200px;
  margin-bottom: 2px;
}

.button-new-tag {
  width: 200px;
  margin-right: 12px;
  line-height: 30px;
  padding-top: 0;
  padding-bottom: 0;
  vertical-align: bottom;

}

.input-new-tag {
  margin-right: 10px;
  width: 200px;
  vertical-align: bottom;
}

#container {
  box-sizing: border-box;
  height: 800px;
  width: 100%;
  margin: 0 0 0 0;
}


#switchLayout {
  height: 30px;
}

.formButton {
  display: flex;
  justify-content: flex-end;
}

.rectangleItem {
  width: 200px;
}

.settingCard {
  height: 400px;
}
</style>