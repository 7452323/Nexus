import {Script,Navigation,NavigationStack,List,VStack,HStack,Text,Button,Image,QRCode,useObservable,useEffect,fetch} from "scripting"

async function getQrCodeToken(){
  const res=await fetch("https://qrcodeapi.115.com/api/1.0/web/1.0/token/")
  const json=await res.json()
  if(json.state!==1||!json.data)throw new Error("获取二维码失败")
  return json.data
}

function View(){
  const dismiss=Navigation.useDismiss()
  const qrImage=useObservable<UIImage|null>(null)
  const statusText=useObservable("正在获取二维码...")
  const cookieResult=useObservable("")

  async function refreshQrCode(){
    statusText.setValue("正在获取二维码...")
    try{
      const data=await getQrCodeToken()
      const image=await QRCode.generate(data.qrcode)
      if(image){qrImage.setValue(image.preparingThumbnail({width:260,height:260})||image)}
      statusText.setValue("请使用115App扫码")
    }catch(e){statusText.setValue("获取失败")}
  }

  useEffect(()=>{refreshQrCode()},[])

  return(
    <NavigationStack>
      <List navigationTitle="115获取Cookie" toolbar={{cancellationAction:<Button title="关闭" action={dismiss}/>}}>
        <VStack alignment="center" spacing={16}>
          <Text>{statusText.value}</Text>
          {qrImage.value?<Image image={qrImage.value}/>:null}
        </VStack>
        {cookieResult.value?<Button title="复制Cookie" action={()=>{Pasteboard.setString(cookieResult.value)}}/>:null}
      </List>
    </NavigationStack>
  )
}

async function run(){await Navigation.present(<View/>);Script.exit()}
run()
