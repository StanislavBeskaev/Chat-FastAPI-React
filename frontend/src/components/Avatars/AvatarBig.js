import React from 'react'
import {Image} from 'react-bootstrap'

import noAvatar from '../../img/no_avatar.png'
import authStore from '../../stores/authStore'
import {observer} from 'mobx-react-lite'

//TODO путь до аватара как параметр
const AvatarBig = () => {
  const avatarSrc = authStore.avatarFile ? `http://localhost:8000/api/static/${authStore.avatarFile}` : noAvatar
  return (
    <Image
      roundedCircle={true}
      src={avatarSrc}
      alt="аватар"
      style={{height: 200, width: 'auto'}}
    />
  )
}

export default observer(AvatarBig)