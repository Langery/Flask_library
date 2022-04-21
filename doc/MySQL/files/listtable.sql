/*
Navicat MySQL Data Transfer

Source Server         : win
Source Server Version : 80028
Source Host           : localhost:3306
Source Database       : flask

Target Server Type    : MYSQL
Target Server Version : 80028
File Encoding         : 65001

Date: 2022-04-21 16:56:02
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for listtable
-- ----------------------------
DROP TABLE IF EXISTS `listtable`;
CREATE TABLE `listtable` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `isLeaf` tinyint(1) NOT NULL,
  `parentid` int DEFAULT NULL,
  `describe` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Records of listtable
-- ----------------------------
INSERT INTO `listtable` VALUES ('1', '第一层', '1', '0', '第一层信息');
INSERT INTO `listtable` VALUES ('2', '第一层 - 一', '0', '1', '第一层 子级一信息');
INSERT INTO `listtable` VALUES ('3', '第一层 - 二', '0', '1', '第一层 子级二信息');
INSERT INTO `listtable` VALUES ('4', '第二层', '1', '0', '第二层');
INSERT INTO `listtable` VALUES ('5', '第二层 - 一', '0', '4', '第二层 子级一信息');
