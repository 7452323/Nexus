import {Circle,Color,Device,HStack,Image,Spacer,Text,VStack,Widget,ZStack,fetch} from 'scripting'
import {solar2lunar,getNextBirthday,getAge,getMeetDays} from './lunar-calendar'

const isDark=Device.colorScheme==='dark'
const ACCENT_COLOR:Color='#fc5ead'

interface Settings{nickname:string;birthday:string;nongli:boolean;eday:string;bless:string;avatarPath:string;ringSize:number;fontName:number;fontAge:number;fontLunar:number;fontQuote:number;fontMeetDays:number;padding:number;ringStroke:number;colorName:string;colorAge:string;colorLunar:string;colorQuote:string;cornerPhotoPath:string;cornerPhotoSize:number;cornerPhotoOffsetX:number;cornerPhotoOffsetY:number}

function loadSettings():Settings{const saved=Storage.get<string>('birthday_settings');if(saved){try{return JSON.parse(saved)}catch{}}return{nickname:'小可爱',birthday:'2000-01-01',nongli:false,eday:'',bless:'',avatarPath:'',ringSize:52,fontName:16,fontAge:11,fontLunar:10,fontQuote:10,fontMeetDays:20,padding:12,ringStroke:2.5,colorName:'',colorAge:'',colorLunar:'',colorQuote:'',cornerPhotoPath:'',cornerPhotoSize:52,cornerPhotoOffsetX:8,cornerPhotoOffsetY:0}}

function WidgetView(){
  const s=loadSettings()
  return(
    <VStack padding={s.padding}>
      <Text font={s.fontName}>{s.nickname||'小可爱'}</Text>
      <Text font={s.fontAge}>年龄: 25岁</Text>
      <Text font={s.fontLunar}>农历: 正月十五</Text>
    </VStack>
  )
}

async function main(){
  const now=new Date()
  const nextMidnight=new Date(now.getFullYear(),now.getMonth(),now.getDate()+1,0,0,0)
  Widget.present(<WidgetView/>,{reloadPolicy:{policy:'after',date:nextMidnight}})
}
main()
