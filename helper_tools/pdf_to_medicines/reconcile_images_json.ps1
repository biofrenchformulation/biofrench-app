$ErrorActionPreference='Stop'
$assets='C:\Work\Documents\XColl\Personal\BioFrench\biofrench-app\app\src\main\assets'
$imgDir=Join-Path $assets 'images'
$medPath=Join-Path $assets 'medicines.json'
$backup=Join-Path $assets 'medicines.json.pre-image-reconcile.bak'
$namesOut='C:\Work\Documents\XColl\Personal\BioFrench\biofrench-app\helper_tools\pdf_to_medicines\image_names_from_assets.txt'

function Norm([string]$s){ return (($s.ToLower() -replace '[^a-z0-9]','')) }
function AlphaKey([string]$s){ return (($s.ToLower() -replace '[^a-z]','')) }

$imgFiles=Get-ChildItem $imgDir -File | Where-Object { $_.Extension.ToLower() -in @('.jpg','.jpeg','.png','.svg') }
$stems=$imgFiles | Select-Object -ExpandProperty BaseName -Unique | Sort-Object
$stems | Set-Content -Encoding UTF8 $namesOut

$meds=Get-Content $medPath | ConvertFrom-Json

$byStem=@{}
foreach($f in $imgFiles){ if(-not $byStem.ContainsKey($f.BaseName)){ $byStem[$f.BaseName]=$f } }
$byNorm=@{}
foreach($f in $imgFiles){ $k=Norm $f.BaseName; if(-not $byNorm.ContainsKey($k)){ $byNorm[$k]=@() }; $byNorm[$k]+=,$f }

$updated=0
$kept=0
$unmatched=@()
$seenIds=@{}
foreach($m in $meds){
  $id=[string]$m.id
  $brand=[string]$m.brandName
  $chosen=$null

  if($byStem.ContainsKey($id)){ $chosen=$id }
  else {
    $nk=Norm $id
    if($byNorm.ContainsKey($nk) -and $byNorm[$nk].Count -eq 1){ $chosen=$byNorm[$nk][0].BaseName }
    else {
      $bk=Norm $brand
      if($byNorm.ContainsKey($bk) -and $byNorm[$bk].Count -eq 1){ $chosen=$byNorm[$bk][0].BaseName }
    }
  }

  if($chosen){
    if($chosen -ne $id){
      if(-not $seenIds.ContainsKey($chosen)){
        $m.id=$chosen
        $updated++
      } else {
        $unmatched += $id
      }
    } else {
      $kept++
    }
    $seenIds[$m.id]=1
  } else {
    $unmatched += $id
    $seenIds[$id]=1
  }
}

Copy-Item $medPath $backup -Force
$meds | ConvertTo-Json -Depth 10 | Set-Content -Path $medPath -Encoding UTF8

$meds2=Get-Content $medPath | ConvertFrom-Json
$createdAliases=0
foreach($m in $meds2){
  $id=[string]$m.id
  $exact=$null
  foreach($ext in @('.jpg','.jpeg','.png','.svg')){ $p=Join-Path $imgDir ($id+$ext); if(Test-Path $p){ $exact=$p; break } }
  if($exact){ continue }

  $alpha=AlphaKey $id
  if(-not $alpha){ continue }

  $cands=$imgFiles | Where-Object { (AlphaKey $_.BaseName) -eq $alpha }
  if($cands.Count -eq 1){
    $src=$cands[0]
    $dst=Join-Path $imgDir ($id + $src.Extension.ToLower())
    if(-not (Test-Path $dst)){
      Copy-Item $src.FullName $dst
      $createdAliases++
    }
  }
}

$finalMissing=@()
$meds3=Get-Content $medPath | ConvertFrom-Json
foreach($m in $meds3){
  $ok=$false
  foreach($ext in @('.jpg','.jpeg','.png','.svg')){ if(Test-Path (Join-Path $imgDir ($m.id+$ext))){ $ok=$true; break } }
  if(-not $ok){ $finalMissing += $m.id }
}

Write-Host "image_names_extracted=$($stems.Count)"
Write-Host "names_file=$namesOut"
Write-Host "json_ids_updated=$updated"
Write-Host "json_ids_kept_exact=$kept"
Write-Host "json_backup=$backup"
Write-Host "image_aliases_created=$createdAliases"
Write-Host "final_missing=$($finalMissing.Count)"
if($finalMissing.Count -gt 0){ $finalMissing | Select-Object -First 30 }
