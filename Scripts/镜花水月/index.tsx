import {Navigation,Script,TabView,Tab,VStack,HStack,Text,Button,TextField,Spacer,ScrollView,Image,LazyVGrid,ProgressView,useState,useEffect,fetch,VideoPlayer,NavigationStack,List,Section} from "scripting"

const KEY_SEC_UID="douyin_sec_uid";const KEY_HISTORY="douyin_history";const KEY_SAVED_USERS="douyin_saved_users";const KEY_COOKIE="douyin_cookie"

const MOBILE_UA="Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15"

function sleep(ms:number){return new Promise(r=>setTimeout(r,ms))}

function loadSecUid():string{return Storage.get<string>(KEY_SEC_UID)||""}
function saveSecUid(uid:string){Storage.set(KEY_SEC_UID,uid)}

function HomeView({dismissApp}:{dismissApp:()=>void}){
  const [videos,setVideos]=useState<any[]>([])
  const [loading,setLoading]=useState(false)
  const [error,setError]=useState("")
  
  async function doLoad(){
    const uid=loadSecUid()
    if(!uid){setError("请先设置抖音号");return}
    setLoading(true);setError("")
    try{
      const cookie=(Storage.get<string>(KEY_COOKIE)||"").trim()
      const resp=await fetch(`https://www.douyin.com/aweme/v1/web/aweme/post/?device_platform=web&aid=6383&sec_user_id=${encodeURIComponent(uid)}&count=21&cookie_enabled=true`,{headers:{"User-Agent":MOBILE_UA,"Cookie":cookie,"Accept":"application/json"}})
      if(!resp.ok)throw new Error(`HTTP${resp.status}`)
      const text=await resp.text()
      const data=JSON.parse(text)
      if(data.status_code!==0)throw new Error(data.status_msg||"API错误")
      const list=(data.aweme_list||[]).map((item:any)=>({aweme_id:item.aweme_id,desc:item.desc||"",cover:item.video?.cover?.url_list?.filter((u:string)=>u.startsWith("https://"))?.pop()||"",play_url:item.video?.play_addr?.url_list?.filter((u:string)=>u.startsWith("https://"))?.pop()||"",digg_count:item.statistics?.digg_count||0}))
      setVideos(list)
    }catch(e){setError((e as Error).message)}
    setLoading(false)
  }
  
  useEffect(()=>{doLoad()},[])
  
  return(
    <NavigationStack>
      <List navigationTitle="抖音作品" toolbar={{topBarLeading:<Button title="关闭" action={()=>dismissApp()}/>,topBarTrailing:<Button title="刷新" action={doLoad}/>}}>
        {error?<Section><Text>{error}</Text></Section>:null}
        {loading?<Section><ProgressView/><Text>加载中...</Text></Section>:null}
        {!loading&&videos.length>0?<Section>{videos.map((v:any)=><HStack key={v.aweme_id}><VStack frame={{width:100,height:150}} background="systemGray5">{v.cover?<Image imageUrl={v.cover} resizable frame={{maxWidth:"infinity",maxHeight:"infinity"}}/>:null}</VStack><VStack><Text lineLimit={2}>{v.desc}</Text></VStack></HStack>)}</Section>:null}
      </List>
    </NavigationStack>
  )
}

function SettingsView(){
  const [inputValue,setInputValue]=useState("")
  
  async function handleSave(){
    const t=inputValue.trim()
    if(!t)return
    saveSecUid(t)
    Storage.set(KEY_SEC_UID,t)
    setInputValue("")
  }
  
  return(
    <NavigationStack>
      <List navigationTitle="设置">
        <Section title="添加抖音号">
          <TextField title="抖音号" prompt="粘贴抖音号/link/sec_uid" value={inputValue} onChanged={(v)=>setInputValue(v)}/>
          <Button title="保存" action={handleSave} disabled={!inputValue.trim()}/>
        </Section>
      </List>
    </NavigationStack>
  )
}

function App(){
  const dismiss=Navigation.useDismiss()
  return(<TabView><Tab title="作品" systemImage="rectangle.grid.2x2"><HomeView dismissApp={()=>dismiss()}/></Tab><Tab title="设置" systemImage="gear"><SettingsView/></Tab></TabView>)
}

async function run(){await Navigation.present({element:<App/>,modalPresentationStyle:'overFullScreen'});Script.exit()}
run()
