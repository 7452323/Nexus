import {VStack,HStack,Text,Image,Spacer,Widget,fetch} from 'scripting'

const CONFIG_PATH=FileManager.appGroupDocumentsDirectory+'/bottom_bar_config.json'

interface Config{weatherBgColor:string|null;contentBgColor:string|null}
function loadConfig():Config{try{const c=FileManager.readAsStringSync(CONFIG_PATH);return c?JSON.parse(c):{weatherBgColor:null,contentBgColor:null}}catch{return{weatherBgColor:null,contentBgColor:null}}}

async function main(){
  const config=loadConfig()
  Widget.present(
    <VStack padding={{leading:16,trailing:16,top:12,bottom:12}} frame={{maxWidth:'infinity',maxHeight:'infinity'}} spacing={10}>
      <HStack alignment="center" padding={{leading:16,trailing:18,top:12,bottom:12}} background={{style:'rgba(239,235,233,0.6)' as any,shape:{type:'rect',cornerRadius:23}}}>
        <Image systemName="cloud.fill" font={38} foregroundStyle="#8C7CFF" frame={{width:38,height:38}}/>
        <VStack alignment="leading" spacing={2}>
          <Text font={14} foregroundStyle="#8C7CFF" bold>天气</Text>
          <Text font={13} foregroundStyle='rgba(0,0,0,0.7)'>加载天气数据...</Text>
        </VStack>
      </HStack>
      <HStack alignment="center" padding={{leading:18,trailing:18,top:12,bottom:12}} background={{style:'rgba(239,235,233,0.6)' as any,shape:{type:'rect',cornerRadius:23}}}>
        <Text font={12.5} foregroundStyle='rgba(0,0,0,0.85)'>每日一句加载中...</Text>
      </HStack>
    </VStack>,
    {policy:'after',date:new Date(Date.now()+30*60*1000)}
  )
}
main()
