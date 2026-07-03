import {Script,Navigation,NavigationStack,List,Section,VStack,HStack,ZStack,Text,Image,Button,TextField,Widget,useState} from 'scripting'

const STORAGE_KEY_API_KEY="qweather_api_key"

function loadApiKey():string{return Storage.get<string>(STORAGE_KEY_API_KEY)||""}
function saveApiKey(value:string){if(value.trim()){Storage.set(STORAGE_KEY_API_KEY,value.trim());return true}return false}

function MainPage(){
  const [apiKey,setApiKey]=useState(loadApiKey())
  const [saved,setSaved]=useState(false)
  const [errorMsg,setErrorMsg]=useState("")
  const dismiss=Navigation.useDismiss()
  const hasSavedKey=loadApiKey().length>0

  function handleSave(){const key=apiKey.trim();if(!key){setErrorMsg("请输入APIKey");return}if(key.length<10){setErrorMsg("APIKey格式不正确");return}saveApiKey(key);setSaved(true);setErrorMsg("");setTimeout(()=>setSaved(false),2000)}

  return(
    <NavigationStack>
      <List navigationTitle="和风天气Widget" toolbar={{cancellationAction:<Button title="完成" action={dismiss}/>}}>
        <Section>
          <VStack alignment="center" spacing={8} padding={20} frame={{maxWidth:"infinity"}}>
            <Image systemName="cloud.sun.fill" frame={{width:56,height:56}} foregroundStyle={{primary:"#FF9A56",secondary:"#6FB1FC"}}/>
            <Text font="title2">和风天气Widget</Text>
            <Text font="subheadline" foregroundStyle="secondaryLabel">精美天气小组件</Text>
            {hasSavedKey?<Text font="caption" foregroundStyle="systemGreen">APIKey已配置</Text>:<Text font="caption" foregroundStyle="systemRed">请先配置APIKey</Text>}
          </VStack>
        </Section>
        <Section header={<Text>APIKey设置</Text>}>
          <TextField title="APIKey" value={apiKey} onChanged={(v)=>{setApiKey(v);setErrorMsg("")}} prompt="粘贴APIKey"/>
          <Button title={saved?"已保存！":"保存APIKey"} action={handleSave}/>
          {errorMsg?<Text font="footnote" foregroundStyle="systemRed">{errorMsg}</Text>:null}
          {hasSavedKey&&<Button title="清除Key" role="destructive" action={()=>{Storage.remove(STORAGE_KEY_API_KEY);setApiKey("");setSaved(false)}}/>}
        </Section>
      </List>
    </NavigationStack>
  )
}

async function run(){await Navigation.present(<MainPage/>);Script.exit()}
run()
