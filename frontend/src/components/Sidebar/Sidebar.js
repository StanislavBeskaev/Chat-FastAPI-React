import React, {useState} from 'react'
import {Link} from 'react-router-dom'
import {Tab, Nav, Button, Row, Modal} from 'react-bootstrap'
import {observer} from 'mobx-react-lite'

import AvatarMini from '../Avatars/AvatarMini'
import authStore from '../../stores/authStore'
import Chats from './Chats'
import Contacts from './Contacts'
import contactModalStore from '../../stores/modals/contactModalStore'
import ContactModal from '../Modals/ContactModal'
import ConfirmDeleteContactModal from '../Modals/ConfirmDeleteContactModal'
import confirmDeleteContactModalStore from '../../stores/modals/confirmDeleteContactModalStore'
import NewChatModal from '../Modals/NewChatModal'
import newChatModalStore from '../../stores/modals/newChatModalStore'
import changeChatNameModalStore from '../../stores/modals/changeChatNameModalStore'
import ChangeChatNameModal from '../Modals/ChangeChatNameModal'


const CHATS_KEY = 'chats'
const CONTACTS_KEY = 'contacts'

function Sidebar({ login }) {
  const [activeKey, setActiveKey] = useState(CHATS_KEY)

  return (
    <div style={{width: '290px'}} className="d-flex flex-column">
      <Tab.Container activeKey={activeKey} onSelect={setActiveKey}>
        <Nav variant="tabs" className="justify-content-center">
          <Nav.Item>
            <Nav.Link eventKey={CHATS_KEY} className="btn">Чаты</Nav.Link>
          </Nav.Item>
          <Nav.Item>
            <Nav.Link eventKey={CONTACTS_KEY} className="btn">Контакты</Nav.Link>
          </Nav.Item>
        </Nav>
        <Tab.Content className="border-end overflow-auto flex-grow-1">
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
              <AvatarMini fileName={authStore.avatarFile}/>
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
                onClick={() => authStore.logout()}
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
      <Modal show={changeChatNameModalStore.show} onHide={() => changeChatNameModalStore.close()}>
        <ChangeChatNameModal />
      </Modal>
    </div>
  )
}

export default observer(Sidebar)
