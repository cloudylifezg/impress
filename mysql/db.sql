grant all on *.* to dbwriter@"localhost" identified by "dbwriter";
grant select on *.* to dbreader@"localhost" identified by "dbreader";
flush privileges;
CREATE DATABASE `impress` /*!40100 DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci */;
CREATE TABLE `impress_news_source` (
  `source_id` int(11) NOT NULL AUTO_INCREMENT,
  `source_name` varchar(30) NOT NULL COMMENT '来源名称',
  `category` tinyint(4) NOT NULL COMMENT '来源种类, 1为微博, 2为新闻, 3为论坛',
  `level_value` decimal(11,2) DEFAULT '0.00' COMMENT '来源等级(网站流量)',
  `rank` tinyint(4) NOT NULL,
  PRIMARY KEY (`source_id`),
  UNIQUE KEY `source_name` (`source_name`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
CREATE TABLE `impress_news_info` (
  `doc_id` int(11) NOT NULL AUTO_INCREMENT,
  `source_id` int(11) NOT NULL COMMENT '来源id',
  `news_id` int(11) NOT NULL COMMENT '消息id',
  `category` varchar(20) NOT NULL COMMENT '消息分类',
  `author` varchar(32) NOT NULL COMMENT '消息作者',
  `word` varchar(10) NOT NULL COMMENT '消息收录关键词',
  `keywords` varchar(200) NOT NULL COMMENT '消息内容关键词',
  `comment` int(11) NOT NULL COMMENT '评论数',
  `repost` int(11) NOT NULL COMMENT '转播数',
  `like` int(11) NOT NULL COMMENT '喜欢数',
  `source` varchar(40) NOT NULL COMMENT '消息来源',
  `time` datetime DEFAULT NULL COMMENT '消息发表时间',
  `ctime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`doc_id`),
  UNIQUE KEY `snw` (`source_id`, `news_id`, `word`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8;
CREATE TABLE `impress_news_detail` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `doc_id` int(11) NOT NULL COMMENT '文章id',
  `doc_type` tinyint(4) DEFAULT 1 COMMENT '1为正文, 2为评论',
  `title` varchar(40) DEFAULT NULL COMMENT '文章标题',
  `content` varchar(4000) NOT NULL COMMENT '文章内容',
  `title_url` varchar(400) NOT NULL COMMENT '文章url',
  `author_homepage` varchar(100) DEFAULT NULL COMMENT '文章作者主页',
  `ip` varchar(20) DEFAULT NULL COMMENT '文章发表ip',
  `time` datetime DEFAULT NULL COMMENT '文章发表时间',
) ENGINE=MyISAM  DEFAULT CHARSET=utf8;
