// 定义一个深拷贝函数  接收目标target参数
function deepClone(target) {
  // 定义一个变量
  let result
  // 如果当前需要深拷贝的是一个对象的话
  if (typeof target === 'object') {
    // 如果是一个数组的话
    if (Array.isArray(target)) {
      result = [] // 将result赋值为一个数组，并且执行遍历
      for (const i in target) {
        // 递归克隆数组中的每一项
        result.push(deepClone(target[i]))
      }
      // 判断如果当前的值是null的话；直接赋值为null
    } else if (target === null) {
      result = null
      // 判断如果当前的值是一个RegExp对象的话，直接赋值
    } else if (target.constructor === RegExp) {
      result = target
    } else {
      // 否则是普通对象，直接for in循环，递归赋值对象的所有值
      result = {}
      for (const i in target) {
        result[i] = deepClone(target[i])
      }
    }
    // 如果不是对象的话，就是基本数据类型，那么直接赋值
  } else {
    result = target
  }
  // 返回最终结果
  return result
}

// 处理数值千分位
function numberFormat(number, decimals = 3, dec_point = '.', thousands_sep = ',') {
  /*
  * 参数说明：
  * number：要格式化的数字
  * decimals：保留几位小数
  * dec_point：小数点符号
  * thousands_sep：千分位符号
  * */
  number = (number + '').replace(/[^0-9+-Ee.]/g, '');
  var n = !isFinite(+number) ? 0 : +number,

    prec = !isFinite(+decimals) ? 0 : Math.abs(decimals),
    sep = (typeof thousands_sep === 'undefined') ? ',' : thousands_sep,
    dec = (typeof dec_point === 'undefined') ? '.' : dec_point,
    s = '',
    toFixedFix = function (n, prec) {
      var k = Math.pow(10, prec);
      return '' + Math.floor(n * k) / k;
    };
  s = (prec ? toFixedFix(n, prec) : '' + Math.floor(n)).split('.');
  var re = /(-?\d+)(\d{3})/;
  console.log(s)
  while (re.test(s[0])) {
    s[0] = s[0].replace(re, "$1" + sep + "$2");
  }

  if ((s[1] || '').length < prec) {
    s[1] = s[1] || '';
    s[1] += new Array(prec - s[1].length + 1).join('0');
  }
  return s.join(dec);
}
// numberFormat(1234567.089, 2, ".", ",");//1,234,567.08

// 时间戳格式转换
function timestampFormat(timestamp) {
  const time = new Date(timestamp * 1000)
  const y = time.getFullYear()
  const m = time.getMonth() + 1
  const d = time.getDate();
  return y + "-" + (m < 10 ? "0" + m : m) + "-" + (d < 10 ? "0" + d : d) + " " + time.toTimeString().substr(0, 8);
}

function copyContent(Content) {
  let transfer = document.createElement('input');
  document.body.appendChild(transfer);
  transfer.value = Content  // 这里表示想要复制的内容
  transfer.select();
  if (document.execCommand('copy')) {
    transfer.blur();
    console.log('复制成功');
    document.body.removeChild(transfer);
    return true
  } else {
    return false
  }

}

function randomNum(minNum, maxNum) {
  switch (arguments.length) {
    case 1:
      return parseInt(Math.random() * minNum + 1, 10);
      break;
    case 2:
      return parseInt(Math.random() * (maxNum - minNum + 1) + minNum, 10);
      break;
    default:
      return 0;
      break;
  }
}

// 16进制颜色转换为RGB
function colorRgb(sColor){
  sColor = sColor.toLowerCase();
  //十六进制颜色值的正则表达式
  var reg = /^#([0-9a-fA-f]{3}|[0-9a-fA-f]{6})$/;
  // 如果是16进制颜色
  if (sColor && reg.test(sColor)) {
      if (sColor.length === 4) {
          var sColorNew = "#";
          for (var i=1; i<4; i+=1) {
              sColorNew += sColor.slice(i, i+1).concat(sColor.slice(i, i+1));    
          }
          sColor = sColorNew;
      }
      //处理六位的颜色值
      var sColorChange = [];
      for (var i=1; i<7; i+=2) {
          sColorChange.push(parseInt("0x"+sColor.slice(i, i+2)));    
      }
      // return "RGB(" + sColorChange.join(",") + ")";
      return  sColorChange.join(",") 

  }
  return sColor;
};

// 对象中值数字类型的字符串转为数字
function objValueStr2Num(obj){
  for (var key in obj){
    if (Number(obj[key])){
      obj[key] = Number(obj[key])
    }
  }
}

export { deepClone, numberFormat, timestampFormat, copyContent,randomNum,colorRgb,objValueStr2Num};
