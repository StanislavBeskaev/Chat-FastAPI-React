import React from 'react'
import {observer} from 'mobx-react-lite'

import AvatarChange from './AvatarChange'
import UserDataChange from './UserDataChange'


const UserData = () => {
  return (
    <div style={{maxWidth: '75%'}} className="p-5 d-flex flex-column flex-grow-1 gap-2">
      <UserDataChange />
      <AvatarChange />
    </div>
  )
}

export default observer(UserData)