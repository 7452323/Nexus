import {NavigationStack,Navigation,Form,Section,Text,Button,Toggle,HStack,VStack,Widget,Script} from 'scripting'

const CONFIG_PATH=FileManager.appGroupDocumentsDirectory+'/bottom_bar_config.json'

interface Config{useTransparentBackground:boolean;showSolarTerms:'auto'|'always'|'never';refreshIntervalMinutes:number;weatherBgColor:string|null;contentBgColor:string|null}

function defaultConfig():Config{return{useTransparentBackground:false,showSolarTerms:'auto',refreshIntervalMinutes:30,weatherBgColor:null,contentBgColor:null}}
function loadConfig():Config{try{const c=FileManager.readAsStringSync(CONFIG_PATH);return c?JSON.parse(c):defaultConfig()}catch{return defaultConfig()}}
function saveConfig(config:Config){try{FileManager.writeAsStringSync(CONFIG_PATH,JSON.stringify(config,null,2))}catch(e){console.error('保存失败:',e)}}

function SettingsView(){
  const config=loadConfig()
  return(
    <NavigationStack>
      <Form>
        <Section title="外观设置">
          <Toggle title="透明背景" value={config.useTransparentBackground} onChanged={(v)=>{config.useTransparentBackground=v;saveConfig(config)}}/>
        </Section>
        <Section header={<Text>操作</Text>}>
          <Button title="预览小组件" systemImage="rectangle.3.group" action={async()=>{try{await Widget.preview({family:'systemMedium'})}catch{}}}/>
        </Section>
      </Form>
    </NavigationStack>
  )
}

async function run(){await Navigation.present(<SettingsView/>);Script.exit()}
run()
