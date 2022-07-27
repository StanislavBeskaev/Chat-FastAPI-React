import React from 'react'
import {Modal} from 'react-bootstrap'
import {observer} from 'mobx-react-lite'

import contactModalStore from '../../stores/modals/contactModalStore'
import ContactModal from '../Modals/ContactModal'
import confirmDeleteContactModalStore from '../../stores/modals/confirmDeleteContactModalStore'
import ConfirmDeleteContactModal from '../Modals/ConfirmDeleteContactModal'
import newChatModalStore from '../../stores/modals/newChatModalStore'
import NewChatModal from '../Modals/NewChatModal'

import SidebarFooter from './SidebarFooter'
import SidebarBody from './SidebarBody/SidebarBody'


function Sidebar({ login }) {
  return (
    <div style={{maxWidth: '25%'}} className="d-flex flex-column flex-grow-1">
      <SidebarBody />
      <SidebarFooter login={login} />
      {/*TODO Подумать где расположить модалки*/}
      <Modal show={contactModalStore.show} onHide={() => contactModalStore.close()}>
        <ContactModal/>
      </Modal>
      {/* TODO внести этот функционал в ConfirmDeleteModal */}
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
