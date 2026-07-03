import {Script,Navigation,NavigationStack,List,Text,HStack,VStack,Image,TextField,Section,Button,Picker,useState,useEffect,useRef,Group,NavigationLink,ScrollView,ZStack,Spacer} from "scripting"
import {fetch} from "scripting"

const countries=["中国","美国","日本","英国","香港","韩国","台湾","德国","法国","加拿大","澳大利亚","新加坡","俄罗斯","巴西","印度"]
const countryCodes=["cn","us","jp","gb","hk","kr","tw","de","fr","ca","au","sg","ru","br","in"]

async function searchApps(term:string,country:string,limit:number=15):Promise<any[]>{
  const encoded=encodeURIComponent(term.trim())
  const response=await fetch(`https://itunes.apple.com/search?term=${encoded}&entity=software&country=${country}&limit=${limit}`)
  if(!response.ok)throw new Error(`搜索失败(HTTP${response.status})`)
  const data=await response.json()
  return (data.results||[]).filter((r:any)=>r.trackId&&r.bundleId)
}

function SearchView(){
  const [searchText,setSearchText]=useState("")
  const [results,setResults]=useState<any[]>([])
  const [loading,setLoading]=useState(false)
  const [countryIdx,setCountryIdx]=useState(0)
  const dismiss=Navigation.useDismiss()

  useEffect(()=>{
    const trimmed=searchText.trim()
    if(!trimmed){setResults([]);return}
    const timer=setTimeout(async()=>{
      setLoading(true)
      try{const apps=await searchApps(trimmed,countryCodes[countryIdx]);setResults(apps)}catch{}
      setLoading(false)
    },300)
    return ()=>clearTimeout(timer)
  },[searchText,countryIdx])

  return(
    <NavigationStack>
      <List navigationTitle="App Search" toolbar={{topBarTrailing:<Button title="关闭" action={dismiss}/>}}>
        <Section>
          <TextField title="" value={searchText} onChanged={setSearchText} prompt="搜索App名称..."/>
          <Picker title="国家/地区" value={countryIdx} onChanged={(v:number)=>setCountryIdx(v)} pickerStyle="menu">
            {countries.map((n,i)=><Text key={i} tag={i}>{n}({countryCodes[i].toUpperCase()})</Text>)}
          </Picker>
        </Section>
        {loading?<Section><Text>搜索中…</Text></Section>:null}
        {!loading&&results.length>0?<Section>{results.map((app:any)=><NavigationLink key={app.trackId} destination={<VStack><Text>App详情: {app.trackName}</Text></VStack>}><HStack><Image imageUrl={app.artworkUrl60} frame={{width:48,height:48}} clipShape={{type:'rect',cornerRadius:10}}/><VStack><Text>{app.trackName}</Text></VStack></HStack></NavigationLink>)}</Section>:null}
      </List>
    </NavigationStack>
  )
}

async function run(){await Navigation.present(<SearchView/>);Script.exit()}
run()
