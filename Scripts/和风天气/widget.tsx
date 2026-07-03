import {VStack,HStack,ZStack,Text,Image,Widget,Spacer,fetch} from 'scripting'

function getApiKey():string{return Storage.get<string>("qweather_api_key")||""}

async function main(){
  const apiKey=getApiKey()
  if(!apiKey){Widget.present(<VStack alignment="center"><Text>请先配置API Key</Text></VStack>);return}
  
  let location=Widget.parameter
  if(!location){
    try{
      await Location.setAccuracy("best")
      const loc=await Location.requestCurrent({forceRequest:false})
      if(loc)location=`${loc.longitude.toFixed(4)},${loc.latitude.toFixed(4)}`
    }catch{}
    if(!location){
      Widget.present(<VStack alignment="center"><Text>无法获取位置</Text></VStack>)
      return
    }
  }
  
  try{
    const res=await fetch(`https://devapi.qweather.com/v7/weather/now?location=${location}&key=${apiKey}`)
    const data=await res.json()
    if(data.code==="200"){
      Widget.present(
        <ZStack>
          <VStack frame={{maxWidth:"infinity",maxHeight:"infinity"}} background="ultraThinMaterial"/>
          <VStack spacing={0} padding={{horizontal:14,vertical:12}}>
            <Text font={42} bold>{data.now.temp}°</Text>
            <Text font="subheadline">{data.now.text}</Text>
          </VStack>
        </ZStack>
      )
    }else{
      Widget.present(<VStack alignment="center"><Text>天气数据加载失败</Text></VStack>)
    }
  }catch{
    Widget.present(<VStack alignment="center"><Text>网络错误</Text></VStack>)
  }
}
main()
