import React, {useState} from 'react'
import addContactModalStore from '../../../stores/modals/addContactModalStore'
import UserAvatar from '../../Avatars/UserAvatar'
import {Badge, Button, ListGroup} from 'react-bootstrap'
import chatMembersModalStore from '../../../stores/modals/chatMembersModalStore'


const ChatMember = ({member, isMe, isChatOwner, canDeleteChatMember, chatId}) => {
  const  [showDeleteBtn, setShowDeleteBtn] = useState(false)

  return (
    <ListGroup.Item
      key={member.login}
      className="d-flex justify-content-between align-items-center"
      onMouseOver={() => setShowDeleteBtn(true)}
      onMouseOut={() => setShowDeleteBtn(false)}
    >
      <div className="d-flex gap-3 align-items-center">
        <div
          onClick={async () => {
            if (isMe) return
            await addContactModalStore.showModalWithLogin(member.login)
          }}
          style={{cursor: !isMe ? 'pointer' : null}}
        >
          <UserAvatar login={member.login} size="sm"/>
        </div>
        {member.login}
        {
          member["is_online"]
            ? <Badge pill bg="success">online</Badge>
            : <Badge pill bg="danger">offline</Badge>
        }
        {
          isMe
            ? <Badge pill bg="info">Вы</Badge>
            : null
        }
        {
          isChatOwner && chatId !== 'MAIN'
            ? <Badge pill bg="primary">Создатель</Badge>
            : null
        }
      </div>
      {
        showDeleteBtn && canDeleteChatMember
          ? <Button
            variant="danger"
            size="sm"
            onClick={() => chatMembersModalStore.deleteChatMember(member.login)}
          >
            X
          </Button>
          : null
      }
    </ListGroup.Item>
  )
}

export default ChatMember