import React, {useState} from 'react'
import {Link} from 'react-router-dom'
import {Tab, Nav, Button, Row, Modal, Image} from 'react-bootstrap'
import {observer} from 'mobx-react-lite'

import authStore from '../../stores/authStore'
import Chats from './Chats'
import Contacts from './Contacts'
import contactModalStore from '../../stores/modals/contactModalStore'
import ContactModal from '../Modals/ContactModal'
import ConfirmDeleteContactModal from '../Modals/ConfirmDeleteContactModal'
import confirmDeleteContactModalStore from '../../stores/modals/confirmDeleteContactModalStore'
import NewChatModal from '../Modals/NewChatModal'
import newChatModalStore from '../../stores/modals/newChatModalStore'

import chats_blue from '../../img/chats_blue.png'
import chats_white from '../../img/chats_white.png'
import contact_blue from '../../img/contact_blue.png'
import contact_white from '../../img/contact_white.png'
import FileAvatar from '../Avatars/FileAvatar'
import messagesStore from '../../stores/messagesStore'
import {useSocket} from '../../contexts/SocketProvider'


const CHATS_KEY = 'chats'
const CONTACTS_KEY = 'contacts'
const ICON_HEIGHT = 30
const PASSIVE_BACKGROUND_COLOR = 'white'
const ACTIVE_BACKGROUND_COLOR = 'dodgerblue'

function Sidebar({ login }) {
  const [activeKey, setActiveKey] = useState(CHATS_KEY)
  const {sendStopTyping} = useSocket()
  const {selectedChatTyping, selectedChatId} = messagesStore

  const logout = async () => {
    if (selectedChatTyping) {
      sendStopTyping(selectedChatId)
    }
    await authStore.logout()
  }

  // TODO побить на кусочки
  return (
    <div style={{maxWidth: '25%'}} className="d-flex flex-column flex-grow-1">
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
        <div className="p-2 border-top border-end small">
          <div className="d-flex flex-column">
            <div>
              <FileAvatar fileName={authStore.avatarFile} size="sm"/>
              <span className="ms-2">
                Ваш логин: <span className="text-muted">{login}</span>
              </span>
            </div>
            <div className="mt-3 d-flex justify-content-end gap-3">
              <Button
                size="sm"
                variant="primary"
                onClick={() => newChatModalStore.open()}
              >
                Новый чат
              </Button>
              <Button
                onClick={logout}
                size="sm"
                variant="danger"
              >
                Выход
              </Button>
            </div>
          </div>
          <Row className="mt-3">
            <Link to="/user-data/">Данные пользователя</Link>
          </Row>
        </div>
      </Tab.Container>
      <Modal show={contactModalStore.show} onHide={() => contactModalStore.close()}>
        <ContactModal/>
      </Modal>
      <Modal show={confirmDeleteContactModalStore.show} onHide={() => confirmDeleteContactModalStore.close()}>
        <ConfirmDeleteContactModal />
      </Modal>
      <Modal show={newChatModalStore.show} onHide={() => newChatModalStore.close()}>
        <NewChatModal />
      </Modal>
    </div>
  )
}

export default observer(Sidebar)
