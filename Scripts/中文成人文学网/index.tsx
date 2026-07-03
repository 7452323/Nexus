import {Script,Navigation,NavigationStack,List,Button,Text,Section,VStack,HStack,ProgressView,TextField,Image,NavigationLink,useState,useEffect} from "scripting"

const SHORT_BASE="https://blog.xbookcn.net"
const LONG_BASE="https://book.xbookcn.net"
const SAFARI_UA="Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15"

async function fetchHTML(url:string):Promise<string>{
  const wv=new WebViewController()
  await wv.setCustomUserAgent(SAFARI_UA)
  await wv.loadURL(url)
  await delay(3000);await wv.waitForLoad()
  const html=await wv.getHTML()??''
  wv.dispose()
  return html
}
function delay(ms:number){return new Promise(r=>setTimeout(r,ms))}

function MainView(){
  const dismiss=Navigation.useDismiss()
  return(
    <NavigationStack>
      <List navigationTitle="xbookcn下载器" toolbar={{cancellationAction:<Button title="关闭" action={dismiss}/>}}>
        <Section title="选择下载来源">
          <NavigationLink destination={<VStack><Text>短篇情色小说</Text></VStack>}><Text>短篇小说</Text></NavigationLink>
          <NavigationLink destination={<VStack><Text>长篇情色小说</Text></VStack>}><Text>长篇小说</Text></NavigationLink>
        </Section>
      </List>
    </NavigationStack>
  )
}

async function run(){await Navigation.present(<MainView/>);Script.exit()}
run()
