import React from 'react'
import {Image} from 'react-bootstrap'

import noAvatar from '../../img/no_avatar.png'
import store from '../../stores/store'
import {observer} from 'mobx-react-lite'

const AvatarMini = () => {
  const avatarSrc = store.avatarFile ? `http://localhost:8000/api/static/${store.avatarFile}` : noAvatar
  return (
    <Image
      roundedCircle={true}
      src={avatarSrc}
      alt="аватар"
      style={{height: 80, width: 'auto'}}
    />
  )
}

export default observer(AvatarMini)