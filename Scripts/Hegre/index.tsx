import {Script,Navigation,NavigationStack,List,TextField,Button,Text,Section,Link,Image,HStack,VStack,Spacer,Group,ProgressView,useObservable,fetch,Response} from "scripting"

declare function openURL(url:string):Promise<boolean>

interface HegreResult{url:string;slug:string;enTitle:string;originalTitle:string;releaseDate:string;runtime:string;plot:string;tagline:string;genres:string[];tags:string[];series:string;posterUrl:string;boardUrl:string}

function generateNfoContent(r:HegreResult):string{
  return`<?xml version="1.0" encoding="UTF-8"?><movie><title>${r.enTitle}</title><originaltitle>${r.originalTitle}</originaltitle><year>${r.releaseDate.substring(0,4)}</year><releasedate>${r.releaseDate}</releasedate><runtime>${r.runtime}</runtime><plot>${r.plot}</plot><genre>${r.genres.join('</genre><genre>')}</genre></movie>`
}

function MainView(){
  const inputText=useObservable("")
  const isLoading=useObservable(false)
  const result=useObservable<HegreResult|null>(null)
  const errorMsg=useObservable("")
  const nfoContent=useObservable("")

  async function handleFetch(){
    const text=inputText.value.trim()
    if(!text){errorMsg.setValue("请输入文件名");return}
    isLoading.setValue(true);errorMsg.setValue("");result.setValue(null);nfoContent.setValue("")
    try{
      const resp=await fetch(`https://www.hegre.com/films/${text.toLowerCase().replace(/[\s.]+/g,'-')}?locale=zh`)
      if(resp.status===200){
        const html=await resp.text()
        const titleMatch=html.match(/<title>(.*?)<\/title>/)
        const title=titleMatch?titleMatch[1].trim()||text:text
        const dateMatch=html.match(/(\d{4}-\d{2}-\d{2})/)
        const date=dateMatch?dateMatch[1]:new Date().toISOString().substring(0,10)
        const r:HegreResult={url:resp.url,slug:text,enTitle:title,originalTitle:title,releaseDate:date,runtime:'29',plot:'',tagline:'',genres:['情色'],tags:['性感','诱惑'],series:'独奏系列',posterUrl:`https://pp.hegre.com/films/${text}/${text}-poster-image-1440x.jpg`,boardUrl:`https://pp.hegre.com/films/${text}/${text}-board-image-3840x.jpg`}
        result.setValue(r)
        nfoContent.setValue(generateNfoContent(r))
      }else{
        errorMsg.setValue("未能找到匹配的Hegre页面")
      }
    }catch(e){errorMsg.setValue(String(e))}
    isLoading.setValue(false)
  }

  return(
    <NavigationStack>
      <List navigationTitle="Hegre NFO Generator" navigationBarTitleDisplayMode="large">
        <Section title="文件名输入">
          <TextField title="文件名" prompt="例如: Hegre.A.Day.In.The.Alya" value={inputText}/>
          <Button title={isLoading.value?"正在获取…":"获取"} action={handleFetch}/>
        </Section>
        {isLoading.value&&<Section><HStack><ProgressView/><Text>正在获取数据…</Text></HStack></Section>}
        {errorMsg.value!==""&&<Section title="错误"><Text>{errorMsg.value}</Text></Section>}
        {result.value&&<>
          <Section title="基本信息">
            <Text>标题: {result.value.enTitle}</Text>
            <Text>日期: {result.value.releaseDate}</Text>
            <Link url={result.value.url}><Text>打开页面</Text></Link>
          </Section>
          <Section title="NFO预览">
            <Text font={10}>{nfoContent.value}</Text>
          </Section>
        </>}
      </List>
    </NavigationStack>
  )
}

async function run(){await Navigation.present(<MainView/>);Script.exit()}
run()
