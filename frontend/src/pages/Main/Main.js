import React from 'react'
import {observer} from 'mobx-react-lite'

import SimpleChat from '../../components/SimpleChat/SimpleChat'


const Main = () => {
  return (
    <SimpleChat />
  )
}

export default observer(Main)