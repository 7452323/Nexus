import {Button,HStack,Image,List,Navigation,NavigationStack,ProgressView,Script,Section,Spacer,Text,TextField,Toolbar,ToolbarItem,VStack,Divider,useState,useEffect} from 'scripting'

const SK={owner:'github_owner',repo:'github_repo',branch:'github_branch',uploadPath:'github_uploadPath',folderName:'github_folderName',commitMessage:'github_commitMessage',history:'github_uploadHistory'}

function UploadPage(){
  const dismiss=Navigation.useDismiss()
  const [owner,setOwner]=useState(Storage.get(SK.owner)??'')
  const [repo,setRepo]=useState(Storage.get(SK.repo)??'')
  const [uploading,setUploading]=useState(false)
  
  async function doUpload(){
    if(!owner.trim()||!repo.trim()){await alert({title:'提示',message:'请填写仓库信息'});return}
    setUploading(true)
    await alert({title:'上传',message:'请选择文件后操作'})
    setUploading(false)
  }

  return(
    <NavigationStack>
      <List navigationTitle="GitHub上传" toolbar={{cancellationAction:<Button title="关闭" action={dismiss}/>}}>
        <Section header={<Text>仓库配置</Text>}>
          <TextField title="Owner" value={owner} onChanged={(v)=>{setOwner(v);Storage.set(SK.owner,v)}} prompt="GitHub用户名"/>
          <TextField title="Repo" value={repo} onChanged={(v)=>{setRepo(v);Storage.set(SK.repo,v)}} prompt="仓库名称"/>
        </Section>
        <Section header={<Text>上传</Text>}>
          <Button title={uploading?'上传中...':'上传到GitHub'} action={doUpload} disabled={uploading}/>
        </Section>
      </List>
    </NavigationStack>
  )
}

async function run(){
  const availability=GitHub.getAvailability()
  if(!availability.available){await alert({title:'GitHub未配置',message:'请在设置中配置Token'});Script.exit()}
  await Navigation.present(<UploadPage/>)
  Script.exit()
}
run()
