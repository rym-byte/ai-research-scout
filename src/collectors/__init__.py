"""数据采集器模块"""
from .hn import HNCollector
from .web import WebCollector

__all__ = ['HNCollector', 'WebCollector']