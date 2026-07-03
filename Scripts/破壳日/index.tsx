import {Button,Color,ColorPicker,HStack,Image,List,Navigation,NavigationStack,Script,Section,Slider,Spacer,Text,TextField,Toggle} from 'scripting'

const DEFAULTS={nickname:'小可爱',birthday:'2000-01-01',nongli:false,eday:'',bless:'',avatarPath:'',ringSize:52,fontName:16,fontAge:11,fontLunar:10,fontQuote:10,fontMeetDays:20,padding:12,ringStroke:2.5,colorName:'',colorAge:'',colorLunar:'',colorQuote:'',cornerPhotoPath:'',cornerPhotoSize:52,cornerPhotoOffsetX:8,cornerPhotoOffsetY:0}

function SettingsPage(){
  const dismiss=Navigation.useDismiss()
  const saved=Storage.get<string>('birthday_settings')
  const settings=(()=>{if(saved){try{return{...DEFAULTS,...JSON.parse(saved)}}catch{}}return{...DEFAULTS}})()
  
  return(
    <NavigationStack>
      <List navigationTitle="破壳日·设置" toolbar={{cancellationAction:<Button title="关闭" action={dismiss}/>}}>
        <Section title="个人信息">
          <HStack><Text>昵称</Text><TextField title="昵称" value={settings.nickname} prompt="输入昵称"/></HStack>
          <HStack><Text>生日</Text><TextField title="生日" value={settings.birthday} prompt="YYYY-MM-DD"/></HStack>
          <HStack><Text>农历生日</Text><Toggle value={settings.nongli}/></HStack>
        </Section>
        <Section title="操作">
          <Button title="保存设置" action={()=>{Storage.set('birthday_settings',JSON.stringify(settings))}}/>
        </Section>
      </List>
    </NavigationStack>
  )
}

async function run(){await Navigation.present(<SettingsPage/>);Script.exit()}
run()
