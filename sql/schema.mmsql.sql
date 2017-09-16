USE MyTest
GO
/* 知识库文章 */
IF EXISTS(SELECT 1 FROM sysobjects WHERE name = 'WK_ARTICLES')
    DROP TABLE WK_ARTICLES
GO
CREATE TABLE WK_ARTICLES(
    ART_ID          NVARCHAR(60)  NOT NULL , 	--主键ID,
    ART_TITLE       NVARCHAR(60) NOT NULL ,   			--'文章标题',
    ART_KEYWORDS    NVARCHAR(200) ,          			--'关键字',
    ART_CONTENT     NVARCHAR(MAX)  ,             			--'内容，Markdown格式',
    CREATE_USER     VARCHAR(40)  NOT NULL  , 			--'创建人',
    CREATE_TIME     DATETIME     NOT NULL DEFAULT GETDATE(),
    UPDATE_USER     VARCHAR(40)  ,           			--'修改人',
    UPDATE_TIME     DATETIME     NOT NULL DEFAULT GETDATE(),
    STATUS          SMALLINT NOT NULL DEFAULT 0,        --'状态 0正常 1删除',
    MATCH_TIMES     INT NOT NULL DEFAULT 0 ,            --被检索到的次数',
    SUPPORT_TIMES   INT   ,                             --支持次数（表示该信息有用）',
    OPPOSE_TIMES    INT   ,                             --'反对次数（表示该信息无用）',
    CANMODI_USERS   VARCHAR(800)  ,                     --'可修改用户',
    CONSTRAINT PRI_WK_ARTICLES PRIMARY KEY (ART_ID)
);

/* 图片 */
IF EXISTS(SELECT 1 FROM sysobjects WHERE name = 'WK_IMAGES')
    DROP TABLE WK_IMAGES
GO
CREATE TABLE WK_IMAGES(
    IMG_ID          NVARCHAR(100)          NOT NULL,      --'主键ID',
    FILENAME        NVARCHAR(100),                          --'文件名',
    FILESIZE        INT,                                   --'文件大小字节数',
    CREATE_USER     NVARCHAR(40) NOT NULL  ,                --'创建人',
    CREATE_TIME     DATETIME   NOT NULL DEFAULT GETDATE(),
    FILEDATA        NVARCHAR(MAX) ,                           --'文件内容BASE64编码',
    CONSTRAINT PK_WK_IMAGES PRIMARY KEY (IMG_ID)
);
IF EXISTS(SELECT 1 FROM sysobjects WHERE name = 'WK_ATTACHS')
    DROP TABLE WK_ATTACHS
GO
/* 文件附件 */
IF EXISTS(SELECT 1 FROM sysobjects WHERE name = 'WK_ATTACHS')
    DROP TABLE WK_ATTACHS
GO
CREATE TABLE WK_ATTACHS(
    ATT_ID          INT         NOT NULL    IDENTITY,      --'主键ID',
    FILENAME        VARCHAR(100)  ,                        --'文件名',
    FILESIZE        INT   ,                                --'文件大小字节数',
    CREATE_USER     VARCHAR(40) NOT NULL ,                 --'创建人',
    CREATE_TIME     DATETIME     NOT NULL DEFAULT GETDATE(),
    FILEDATA        NVARCHAR(MAX),                            --'文件内容BASE64编码',
    CONSTRAINT PK_WK_ATTACHS PRIMARY KEY (ATT_ID)
);
