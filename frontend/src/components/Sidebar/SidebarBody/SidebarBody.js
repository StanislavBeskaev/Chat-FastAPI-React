import React, {useState} from 'react'
import {Image, Nav, Tab} from 'react-bootstrap'
import {observer} from 'mobx-react-lite'

import chats_white from '../../../img/chats_white.png'
import chats_blue from '../../../img/chats_blue.png'
import contact_white from '../../../img/contact_white.png'
import contact_blue from '../../../img/contact_blue.png'
import Chats from './Chats'
import Contacts from './Contacts'


const CHATS_KEY = 'chats'
const CONTACTS_KEY = 'contacts'
const ICON_HEIGHT = 30
const PASSIVE_BACKGROUND_COLOR = 'white'
const ACTIVE_BACKGROUND_COLOR = 'dodgerblue'


const SidebarBody = () => {
  const [activeKey, setActiveKey] = useState(CHATS_KEY)


  return (
    <Tab.Container activeKey={activeKey} onSelect={setActiveKey}>
      <Tab.Content className="border-end overflow-auto flex-grow-1">
        <Nav fill variant="tabs" className="justify-content-center">
          <Nav.Item>
            <Nav.Link
              eventKey={CHATS_KEY}
              className="btn"
              style={{backgroundColor: activeKey === CHATS_KEY ? ACTIVE_BACKGROUND_COLOR : PASSIVE_BACKGROUND_COLOR}}
            >
              <Image
                src={activeKey === CHATS_KEY ? chats_white : chats_blue}
                height={ICON_HEIGHT}
              />
            </Nav.Link>
          </Nav.Item>
          <Nav.Item>
            <Nav.Link
              eventKey={CONTACTS_KEY}
              className="btn"
              style={{backgroundColor: activeKey === CONTACTS_KEY ? ACTIVE_BACKGROUND_COLOR : PASSIVE_BACKGROUND_COLOR}}
            >
              <Image
                src={activeKey === CONTACTS_KEY ? contact_white : contact_blue}
                height={ICON_HEIGHT}
              />
            </Nav.Link>
          </Nav.Item>
        </Nav>
        <Tab.Pane eventKey={CHATS_KEY}>
          <Chats/>
        </Tab.Pane>
        <Tab.Pane eventKey={CONTACTS_KEY}>
          <Contacts />
        </Tab.Pane>
      </Tab.Content>
    </Tab.Container>
  )
}

export default observer(SidebarBody)